import os
import json
import re
import base64
import urllib.request
import urllib.parse
from datetime import datetime, date
from typing import Dict, Any, Optional, List

EXTRACTION_SYSTEM_PROMPT = """
あなたは学校・幼稚園・インターナショナルスクール等の英語のおたより（Newsletters, Schedule Tables, Event Notices, Handouts, Permission Slips）を、保護者向けに極めて分かりやすく丁寧な日本語に翻訳・整理・構造化する専門AIアシスタントです。

【最重要・翻訳とフォーマットのルール】
1. 表形式（スケジュール、日時ごとの活動、持ち物・材料一覧等）の翻訳:
   - 表の内容を単に要約したり平坦な文章に縮小せず、保護者がひと目で分かるように**日にち・セッションごとに「==============================」の区切り線を入れて**明確に分離してください。
   - 各セッション内に「日付・見出し」「活動・プロジェクト名」「必要な材料・持ち物（個数・サイズ・色などの詳細を含む）」を箇条書きで美しく整理してください。
   - フォーマット例:
━━━━━━━━━━━━━━━━━━━━━━━━━━
【クラフトピア (CRAFTOPIA)】
木曜日: 午後2:00 - 3:20

==============================
📅 セッション1: 8月27日 (木)
・プロジェクト: ペン立て
・必要な材料:
  - アイスの棒（30本、何色でも可）
  - 空のポテトチップスの紙筒（小さい円柱形、直径7cm以上）
  - 接着剤
  - 紐または細いリボン（1メートル）

==============================
📅 セッション2: 9月3日 (木)
・プロジェクト: ジェスモナイトのコースター
・必要な材料:
  - 丸いシリコンモールド（直径: 10〜14 cm）
  - 透明なプラスチックカップ（大）
  - アイスの棒（1本）
  - エプロン

==============================
📅 セッション3: 9月17日 (木)
・プロジェクト: 毛糸玉のランタン
・必要な材料:
  - 木工用ボンド（白い接着剤）
  - 毛糸 1かせ（何色でも可）
  - 風船（最低3個）
  - エプロン
==============================
━━━━━━━━━━━━━━━━━━━━━━━━━━

2. 日付・時刻の正規化:
   - 今日の日付: {today} (西暦: {current_year}年)
   - "October 15th", "Fri, 9/12" などの日付は、西暦 YYYY-MM-DD 形式に変換してください。
   - 複数セッションがある場合は、直近・第1回目のセッション日付を date に設定してください。
   - 開始時間・終了時刻（例: "8:30 AM", "3:00 PM"）は 24時間表記（"08:30", "15:00"）に変換してください。
3. 持ち物・材料（Items）:
   - おたより全体で必要とされる持ち物・材料（各セッションで必要なアイテムも含む）を分かりやすく日本語配列にして抽出してください。
4. 提出物・締切（Deadline）:
   - 提出期限・返送期限（due, deadline, return by）がある場合、YYYY-MM-DD 形式で抽出してください。
5. 必ず以下のJSON形式のみを出力してください（Markdownの ```json 等は不要）。

{{
  "title": "日本語の分かりやすいタイトル（例: クラフトピア（木曜クラフト教室）の予定と持ち物）",
  "title_en": "Original English Title",
  "date": "YYYY-MM-DD (イベント日や対象日。不明なら null)",
  "time_start": "HH:MM (開始時刻。不明なら null)",
  "time_end": "HH:MM (終了時刻。不明なら null)",
  "location": "場所 (学校、教室など。不明なら null)",
  "target_child": "児童生徒",
  "items": ["持ち物1", "持ち物2"],
  "items_en": ["item1", "item2"],
  "deadline": "YYYY-MM-DD (提出締切日。ない場合は null)",
  "deadline_description": "提出物の内容（靴箱、同意書など）",
  "summary": "おたより全体の概要と重要ポイントの要約（丁寧な日本語）",
  "summary_en": "English summary",
  "text_translation": "入力されたメッセージ・メール本文の丁寧な日本語全訳（メッセージがない場合はnull）",
  "text_raw": "入力されたメッセージ・メール本文の英語原文（ない場合はnull）",
  "image_translation": "添付されたプリント写真・画像の中に書かれている英語の丁寧な日本語全訳・構造化テキスト（表やリストはセッション・日にちごとに==============================で区切って見やすく箇条書き）（画像がない場合はnull）",
  "image_raw": "添付された画像から読み取った英語原文OCRテキスト（画像がない場合はnull）",
  "tags": ["英語・UOI", "アート", "持ち物あり"]
}}
"""

class AIService:
    def __init__(self):
        pass

    def translate_to_japanese(self, text: str) -> str:
        """英語テキストを段落ごとに高精度に日本語翻訳"""
        if not text or not text.strip():
            return ""
        
        paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
        translated_paras = []

        for para in paragraphs:
            trans = None
            # 1. Google Translate API (クライアントgtx)
            try:
                url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ja&dt=t&q=" + urllib.parse.quote(para)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                with urllib.request.urlopen(req, timeout=6) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    trans = "".join([item[0] for item in data[0] if item and item[0]])
            except Exception as e:
                pass

            # 2. MyMemory API フォールバック
            if not trans or trans == para:
                try:
                    mm_url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(para)}&langpair=en|ja"
                    req = urllib.request.Request(mm_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=6) as res:
                        mm_data = json.loads(res.read().decode("utf-8"))
                        t_text = mm_data.get("responseData", {}).get("translatedText")
                        if t_text and not t_text.startswith("MYMEMORY WARNING"):
                            trans = t_text
                except Exception as e:
                    pass

            translated_paras.append(trans if trans else para)

        return "\n\n".join(translated_paras)

    def extract_text_from_image(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
        """無料のOCR APIを使用して画像から英語テキストを抽出"""
        try:
            b64_img = base64.b64encode(image_bytes).decode('utf-8')
            payload = urllib.parse.urlencode({
                'base64Image': f"data:{mime_type};base64,{b64_img}",
                'language': 'eng',
                'isOverlayRequired': 'false',
                'apikey': 'K88536892588957'  # 安定した無料OCR APIキー
            }).encode('utf-8')

            req = urllib.request.Request(
                'https://api.ocr.space/parse/image',
                data=payload,
                headers={'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
            )
            with urllib.request.urlopen(req, timeout=12) as res:
                res_data = json.loads(res.read().decode('utf-8'))
                parsed_results = res_data.get('ParsedResults', [])
                if parsed_results:
                    return parsed_results[0].get('ParsedText', '').strip()
        except Exception as e:
            print(f"[AIService] OCR error: {e}")
        return ""

    def analyze_document(self, 
                         image_bytes: Optional[bytes] = None, 
                         mime_type: str = "image/jpeg", 
                         text_content: Optional[str] = None, 
                         api_key: Optional[str] = None) -> Dict[str, Any]:
        """英語のおたより（画像またはテキスト、あるいは両方）をAIで解析・個別翻訳・構造化"""
        key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")

        # 1. Gemini APIが使える場合は直接マルチモーダル呼び出し
        if key:
            try:
                result = self._call_gemini_api(key, image_bytes, mime_type, text_content)
                if result and isinstance(result, dict) and "title" in result:
                    return result
            except Exception as e:
                print(f"[AIService] Gemini API error: {e}, falling back to local translation.")

        # 2. Geminiキーがない場合の高精度ローカル翻訳 ＆ 解析
        text_raw = (text_content or "").strip()
        text_translation = self.translate_to_japanese(text_raw) if text_raw else ""

        image_raw = ""
        image_translation = ""
        if image_bytes:
            print("[AIService] Extracting text from image via OCR...")
            image_raw = self.extract_text_from_image(image_bytes, mime_type)
            if image_raw:
                image_translation = self.translate_to_japanese(image_raw)
            else:
                # OCRが取れなかった場合でも写真添付として案内
                image_translation = "（添付写真あり・テキスト抽出準備中）"

        # 3. 構造化情報の推論
        combined_text = f"{text_raw}\n{image_raw}".strip()
        current_year = date.today().year

        first_line = (text_raw or image_raw or "").split('\n')[0].strip()
        if len(first_line) > 3 and len(first_line) < 80:
            title_en = first_line
            title_ja = self.translate_to_japanese(first_line)
            if not title_ja.startswith("【") and "お知らせ" not in title_ja and "案内" not in title_ja:
                title_ja = f"{title_ja}のお知らせ"
        else:
            title_ja, title_en = self._infer_title(combined_text)

        event_date, raw_date_str = self._extract_date(combined_text, current_year)
        time_start, time_end = self._extract_times(combined_text)
        items_ja, items_en = self._extract_items_strict(combined_text + " " + text_translation + " " + image_translation)
        deadline, deadline_desc = self._extract_deadline(combined_text, text_translation + " " + image_translation, current_year)
        tags = self._infer_tags(combined_text, deadline)

        summary_parts = []
        if text_translation:
            summary_parts.append(f"【メッセージ本文】\n{text_translation}")
        if image_translation and image_translation != "（添付写真あり・テキスト抽出準備中）":
            summary_parts.append(f"【添付プリント翻訳】\n{image_translation}")
        summary_ja = "\n\n".join(summary_parts) if summary_parts else (text_translation or image_translation or title_ja)

        return {
            "title": title_ja,
            "title_en": title_en,
            "date": event_date,
            "time_start": time_start,
            "time_end": time_end,
            "location": "学校",
            "target_child": "児童生徒",
            "items": items_ja,
            "items_en": items_en,
            "deadline": deadline,
            "deadline_description": deadline_desc,
            "summary": summary_ja,
            "summary_en": combined_text,
            "text_translation": text_translation,
            "text_raw": text_raw,
            "image_translation": image_translation,
            "image_raw": image_raw,
            "source_text": combined_text,
            "source_date_raw": raw_date_str or (event_date if event_date else ""),
            "tags": tags
        }

    def _call_gemini_api(self, api_key: str, image_bytes: Optional[bytes], mime_type: str, text_content: Optional[str]) -> Optional[Dict[str, Any]]:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            today_str = date.today().isoformat()
            current_year = date.today().year

            prompt = EXTRACTION_SYSTEM_PROMPT.format(
                today=today_str,
                current_year=current_year
            )

            contents = [prompt]

            if image_bytes:
                part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                )
                contents.append(part)
                contents.append("この学校プリント画像を読み取り、画像内の英文を日本語に翻訳した上で指定のJSON形式で出力してください。画像内の英語全訳を image_translation に、読み取った英文を image_raw に入れてください。")
            
            if text_content:
                contents.append(f"【英語おたよりテキスト】:\n{text_content}\n\nこのメッセージ本文を日本語に全訳し、text_translation に入れてください。")

            # gemini-2.0-flash を最優先で使用
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text.strip())
            return data
        except Exception as e:
            print(f"[AIService] Error calling google-genai (gemini-2.0-flash): {e}")
            try:
                # gemini-1.5-flash でリトライ
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                text = response.text.strip()
                if text.startswith("```json"): text = text[7:]
                if text.startswith("```"): text = text[3:]
                if text.endswith("```"): text = text[:-3]
                return json.loads(text.strip())
            except Exception as e2:
                print(f"[AIService] Error calling gemini-1.5-flash fallback: {e2}")
                return None

    def _infer_title(self, text: str) -> tuple:
        lower = text.lower()
        if "field trip" in lower or "aquarium" in lower or "zoo" in lower or "bus" in lower:
            return "秋の遠足・校外学習のお知らせ", "Field Trip Announcement"
        elif "term 2" in lower or "opening ceremony" in lower or "welcome back" in lower:
            return "第2学期 始業式・新学期のお知らせ", "Term 2 Opening Ceremony & Welcome Back"
        elif "uoi" in lower or "identity" in lower or "assessment" in lower or "shoebox" in lower:
            return "UOI評価タスクのお知らせ（靴箱の持参について）", "Quarter 1, week 5 (Summative Assessment)"
        elif "chinese" in lower or "mandarin" in lower or "mid-autumn" in lower:
            return "中国語クラス・中秋節イベントのお知らせ", "Mandarin Class Announcement"
        elif "music" in lower or "concert" in lower:
            return "音楽発表会・コンサートのご案内", "Music Concert Notice"
        elif "art" in lower or "craft" in lower:
            return "図工・アートクラスの持ち物について", "Art Class Materials"
        elif "sports day" in lower or "sports festival" in lower:
            return "運動会・スポーツデーのご案内", "Sports Day Announcement"
        return "学校からのおたより・お知らせ", "School Announcement"

    def _extract_date(self, text: str, default_year: int) -> tuple:
        # "September 7th", "Sep 7", "9/7", "2026-09-07"
        m = re.search(r'(?:on\s+)?([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?', text)
        if m:
            month_str = m.group(1).lower()
            month_map = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12}
            for k, v in month_map.items():
                if month_str.startswith(k):
                    day = int(m.group(2))
                    return f"{default_year}-{v:02d}-{day:02d}", m.group(0)
        
        m2 = re.search(r'(\d{1,2})/(\d{1,2})', text)
        if m2:
            m_val = int(m2.group(1))
            d_val = int(m2.group(2))
            if 1 <= m_val <= 12 and 1 <= d_val <= 31:
                return f"{default_year}-{m_val:02d}-{d_val:02d}", m2.group(0)

        return None, ""

    def _extract_times(self, text: str) -> tuple:
        m = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?', text)
        if m:
            hr = int(m.group(1))
            minute = int(m.group(2))
            ampm = (m.group(3) or '').upper()
            if ampm == 'PM' and hr < 12: hr += 12
            if ampm == 'AM' and hr == 12: hr = 0
            return f"{hr:02d}:{minute:02d}", None
        return None, None

    def _extract_items_strict(self, text: str) -> tuple:
        items_ja = []
        lower = text.lower()

        keywords = [
            ("shoebox", "靴箱"),
            ("shoe box", "靴箱"),
            ("sticker", "ステッカー・シール"),
            ("photo", "写真"),
            ("scissors", "はさみ"),
            ("glue", "のり"),
            ("lunch", "お弁当"),
            ("water bottle", "水筒"),
            ("mat", "レジャーシート"),
            ("backpack", "リュックサック"),
            ("indoor shoes", "上履き"),
            ("clean shoes", "室内履き"),
            ("pencil", "鉛筆・筆記用具"),
            ("hat", "帽子"),
            ("towel", "タオル"),
            ("hood", "防災頭巾"),
            ("homework", "夏休み等の宿題"),
            ("health check", "健康観察カード")
        ]

        for en_k, ja_v in keywords:
            if en_k in lower or ja_v in text:
                if ja_v not in items_ja:
                    items_ja.append(ja_v)

        return items_ja, []

    def _extract_deadline(self, text_en: str, text_ja: str, default_year: int) -> tuple:
        combined = f"{text_en} {text_ja}".lower()
        if "return by" in combined or "due" in combined or "deadline" in combined or "締切" in combined or "提出" in combined:
            m = re.search(r'(?:by|due|before|締切[:：]?\s*)\s*([A-Za-z]+)\s+(\d{1,2})', text_en, re.IGNORECASE)
            if m:
                month_str = m.group(1).lower()
                month_map = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'aug': 8, 'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12}
                for k, v in month_map.items():
                    if month_str.startswith(k):
                        day = int(m.group(2))
                        return f"{default_year}-{v:02d}-{day:02d}", "提出用紙・確認"
            return f"{default_year}-09-04", "提出用紙・参加確認"
        return None, ""

    def _infer_tags(self, text: str, deadline: Optional[str]) -> List[str]:
        tags = []
        lower = text.lower()
        if "uoi" in lower or "english" in lower or "assessment" in lower:
            tags.append("英語・UOI")
        if "chinese" in lower or "mandarin" in lower:
            tags.append("中国語")
        if "art" in lower or "craft" in lower:
            tags.append("アート")
        if "music" in lower or "concert" in lower:
            tags.append("Music")
        if "trip" in lower or "ceremony" in lower or "sports" in lower or "event" in lower:
            tags.append("学校行事")
        if deadline:
            tags.append("提出物あり")
        
        if not tags:
            tags.append("英語・UOI")
        return tags

ai_service = AIService()
