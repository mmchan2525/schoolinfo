import os
import uuid
import shutil
import json
import html
import urllib.parse
from datetime import datetime, date
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import db
from ai_service import ai_service
from sample_data import init_sample_data

app = FastAPI(title="おたよりポスト (Otayori Post)", version="2.0.0")

# CORS許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# 静的ファイルの配信
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 初期サンプルデータのロード
init_sample_data()

# --- Pydantic Models ---
class PostCreate(BaseModel):
    id: Optional[str] = None
    title: str
    title_en: Optional[str] = ""
    date: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    location: Optional[str] = ""
    target_child: Optional[str] = ""
    items: List[str] = []
    items_en: List[str] = []
    deadline: Optional[str] = None
    deadline_description: Optional[str] = ""
    is_submitted: Optional[bool] = False
    summary: str
    summary_en: Optional[str] = ""
    text_translation: Optional[str] = ""
    text_raw: Optional[str] = ""
    image_translation: Optional[str] = ""
    image_raw: Optional[str] = ""
    source_text: Optional[str] = ""
    source_date_raw: Optional[str] = ""
    tags: List[str] = []
    image_url: Optional[str] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    title_en: Optional[str] = None
    date: Optional[str] = None
    time_start: Optional[str] = None
    time_end: Optional[str] = None
    location: Optional[str] = None
    target_child: Optional[str] = None
    items: Optional[List[str]] = None
    items_en: Optional[List[str]] = None
    deadline: Optional[str] = None
    deadline_description: Optional[str] = None
    is_submitted: Optional[bool] = None
    summary: Optional[str] = None
    summary_en: Optional[str] = None
    text_translation: Optional[str] = None
    text_raw: Optional[str] = None
    image_translation: Optional[str] = None
    image_raw: Optional[str] = None
    source_text: Optional[str] = None
    source_date_raw: Optional[str] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None

class SettingsUpdate(BaseModel):
    user_name: Optional[str] = None
    gemini_api_key: Optional[str] = None
    line_notify_token: Optional[str] = None
    notification_time: Optional[str] = None

class LineNotifyRequest(BaseModel):
    post_id: Optional[str] = None
    custom_message: Optional[str] = None

def render_index_html() -> str:
    index_path = os.path.join(STATIC_DIR, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    posts = db.get_all_posts()
    upcoming = db.get_upcoming_events()
    settings = db.get_settings()
    user_name = html.escape(str(settings.get("user_name", "ゲスト")))

    # おたよりカードHTML生成（最新順）
    cards_html = []
    for p in posts:
        p_id = html.escape(str(p.get("id", "")))
        p_title = html.escape(str(p.get("title", "お知らせ")))
        p_title_en = html.escape(str(p.get("title_en", "")))
        p_summary = html.escape(str(p.get("summary") or p.get("text_translation") or p.get("image_translation") or ""))
        p_date_raw = p.get("date")
        p_date_str = f"📅 {p_date_raw.replace('-', '/')}" if p_date_raw else "📅 随時"
        p_img = p.get("image_url") or "/static/samples/no_image.svg"

        tags_html = ""
        for t in p.get("tags", []):
            t_esc = html.escape(str(t))
            color, icon = "bg-stone-100 text-stone-600", "🏷️"
            if "英語" in t or "UOI" in t: color, icon = "bg-blue-100 text-blue-800", "📚"
            elif "中国語" in t: color, icon = "bg-red-100 text-red-800", "🀄"
            elif "アート" in t: color, icon = "bg-purple-100 text-purple-800", "🎨"
            elif "Music" in t: color, icon = "bg-pink-100 text-pink-800", "🎵"
            elif "行事" in t: color, icon = "bg-emerald-100 text-emerald-800", "🏫"
            elif "提出物" in t: color, icon = "bg-amber-100 text-amber-800", "⚠️"
            tags_html += f'<span class="px-2 py-0.5 rounded-md text-[10px] font-bold {color}">{icon} {t_esc}</span>'

        items = p.get("items", [])
        items_badge = f'<span class="text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded font-bold">🎒 持ち物 {len(items)}点</span>' if items else ''
        dl = p.get("deadline")
        dl_badge = f'<span class="text-red-700 bg-red-50 px-1.5 py-0.5 rounded font-bold">⚠️ 締切: {dl.replace("-", "/")}</span>' if dl else ''

        raw_tags = ",".join(p.get("tags", []))
        card = f'''
        <a href="/post/{p_id}" data-tags="{html.escape(raw_tags)}" class="otayori-card block p-3.5 flex gap-3.5 hover:border-amber-300 transition no-underline">
          <div class="w-16 h-20 rounded-xl bg-stone-100 border border-stone-200 overflow-hidden flex-shrink-0 flex items-center justify-center">
            <img src="{p_img}" class="w-full h-full object-cover" alt="プリント">
          </div>
          <div class="flex-1 min-w-0 flex flex-col justify-between">
            <div>
              <div class="flex items-center gap-1.5 flex-wrap">
                {tags_html}
                <span class="text-[10px] text-stone-400 font-semibold ml-auto">{p_date_str}</span>
              </div>
              <h3 class="text-xs font-extrabold text-stone-900 mt-1 truncate leading-tight">{p_title}</h3>
              <p class="text-[10px] text-stone-400 truncate">{p_title_en}</p>
            </div>
            <p class="text-[11px] text-stone-600 line-clamp-2 mt-1 leading-snug">{p_summary}</p>
            <div class="flex items-center justify-between mt-2 pt-1.5 border-t border-stone-100 text-[10px]">
              <div class="flex items-center gap-1.5 truncate max-w-[190px]">
                {items_badge}
                {dl_badge}
              </div>
              <span class="text-emerald-700 font-bold flex items-center gap-0.5 flex-shrink-0">
                <span>詳細</span>
                <span class="text-xs">›</span>
              </span>
            </div>
          </div>
        </a>
        '''
        cards_html.append(card)

    rendered_posts = "\n".join(cards_html) if cards_html else '<div class="text-center py-8 text-stone-400 text-xs">おたよりはありません</div>'

    # 直近の予定HTML生成
    upcoming_html_cards = []
    for ev in upcoming:
        ev_id = html.escape(str(ev.get("id", "")))
        ev_title = html.escape(str(ev.get("title", "")))
        ev_loc = html.escape(str(ev.get("location", "学校")))
        ev_date = ev.get("date", "")
        day_str = ev_date.split("-")[2] if (ev_date and len(ev_date.split("-")) == 3) else "—"
        month_str = f"{int(ev_date.split('-')[1])}月" if (ev_date and len(ev_date.split("-")) == 3) else "—"
        time_str = f"<span>⏰ {ev.get('time_start')}〜</span>" if ev.get("time_start") else ""

        items_tags = "".join([f'<span class="item-tag truncate max-w-[140px]">🎒 {html.escape(str(it).split("(")[0].strip())}</span>' for it in ev.get("items", [])[:3]])

        up_card = f'''
        <a href="/post/{ev_id}" class="otayori-card block p-3.5 flex items-center justify-between gap-3 hover:border-sky-300 transition no-underline">
          <div class="flex items-center gap-3 min-w-0">
            <div class="date-badge">
              <span class="day">{day_str}</span>
              <span class="month">{month_str}</span>
            </div>
            <div class="min-w-0">
              <div class="flex items-center gap-1.5">
                <h4 class="font-extrabold text-xs text-stone-800 truncate">{ev_title}</h4>
              </div>
              <div class="flex items-center gap-1 mt-1 text-[11px] text-stone-500">
                {time_str}
                <span class="truncate">📍 {ev_loc}</span>
              </div>
              <div class="flex flex-wrap gap-1 mt-1.5">
                {items_tags}
              </div>
            </div>
          </div>
          <div class="flex flex-col items-end gap-1 flex-shrink-0">
            <span class="text-emerald-700 font-bold text-xs flex items-center gap-0.5">
              <span>詳細</span>
              <span>›</span>
            </span>
          </div>
        </a>
        '''
        upcoming_html_cards.append(up_card)

    rendered_upcoming = "\n".join(upcoming_html_cards) if upcoming_html_cards else '<div class="text-center py-4 text-stone-400 text-xs">直近の予定はありません</div>'

    # 置換
    import re
    res_html = re.sub(r'<div id="postsList"[^>]*>[\s\S]*?</div>\s*</section>', f'<div id="postsList" class="space-y-3 mt-2">\n{rendered_posts}\n</div>\n</section>', html_template)
    res_html = re.sub(r'<div id="upcomingEventsList"[^>]*>[\s\S]*?</div>\s*</section>', f'<div id="upcomingEventsList" class="space-y-2.5">\n{rendered_upcoming}\n</div>\n</section>', res_html)
    res_html = re.sub(r'<span id="postsCount"[^>]*>.*?</span>', f'<span id="postsCount" class="text-xs text-stone-400 font-semibold">{len(posts)}件</span>', res_html)
    res_html = res_html.replace('id="userNameDisplay">めぐ</span>', f'id="userNameDisplay">{user_name}</span>')

    return res_html

@app.get("/")
def get_index():
    content = render_index_html()
    return HTMLResponse(content=content, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    })

@app.get("/new")
def get_new_post_page():
    return FileResponse(os.path.join(STATIC_DIR, "new.html"), headers={
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    })

@app.get("/post/{post_id}")
def get_post_detail_page(post_id: str):
    post = db.get_post_by_id(post_id)
    if not post:
        posts = db.get_all_posts()
        post = next((p for p in posts if str(p.get("id")) == str(post_id)), None)
    
    if not post:
        raise HTTPException(status_code=404, detail="おたよりが見つかりませんでした")

    title = html.escape(str(post.get("title", "お知らせ")))
    title_en = html.escape(str(post.get("title_en", "")))
    date_val = post.get("date", "")
    date_display = f"📅 {date_val.replace('-', '/')}" if date_val else "📅 随時"
    time_start = post.get("time_start", "")
    time_end = post.get("time_end", "")
    time_display = f"{time_start} 〜 {time_end}" if (time_start and time_end) else (time_start or "終日")
    location = html.escape(str(post.get("location", "学校")))
    deadline = post.get("deadline", "")
    deadline_desc = html.escape(str(post.get("deadline_description", "提出締切")))

    tags_badges = []
    for t in post.get("tags", []):
        t_esc = html.escape(str(t))
        c = "bg-stone-100 text-stone-700"
        if "英語" in t or "UOI" in t: c = "bg-blue-100 text-blue-800"
        elif "中国語" in t: c = "bg-red-100 text-red-800"
        elif "アート" in t: c = "bg-purple-100 text-purple-800"
        elif "Music" in t: c = "bg-pink-100 text-pink-800"
        elif "行事" in t: c = "bg-emerald-100 text-emerald-800"
        elif "提出物" in t: c = "bg-amber-100 text-amber-800"
        tags_badges.append(f'<span class="px-2.5 py-1 rounded-full text-xs font-bold {c}">{t_esc}</span>')
    tags_html = "".join(tags_badges)

    items = post.get("items", [])
    items_html = ""
    if items:
        tags = "".join([f'<span class="px-3 py-1 bg-amber-50 text-amber-800 border border-amber-200/80 rounded-xl text-xs font-bold">🎒 {html.escape(str(it))}</span>' for it in items])
        items_html = f'''
        <div class="p-4 rounded-2xl bg-amber-50/40 border border-amber-200/60 space-y-2">
          <h4 class="text-xs font-extrabold text-amber-900 flex items-center gap-1.5">
            <span>🎒 持ち物・準備するもの</span>
          </h4>
          <div class="flex flex-wrap gap-2 pt-1">{tags}</div>
        </div>
        '''

    # 日時・場所カード
    datetime_html = ""
    if date_val or time_start or location != "学校" or deadline:
        dl_row = f'''
        <div class="flex items-center justify-between text-red-600 font-bold border-t border-red-100 pt-2 text-xs">
          <span>⚠️ 提出締切:</span>
          <span>{deadline.replace('-', '/')} ({deadline_desc})</span>
        </div>
        ''' if deadline else ""

        datetime_html = f'''
        <div class="p-4 rounded-2xl bg-stone-50 border border-stone-200/80 space-y-2.5 text-xs">
          <div class="flex items-center justify-between">
            <span class="text-stone-500">📅 日程:</span>
            <span class="font-bold text-stone-800">{date_display}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-stone-500">⏰ 時間:</span>
            <span class="font-bold text-stone-800">{time_display}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-stone-500">📍 場所:</span>
            <span class="font-bold text-stone-800">{location}</span>
          </div>
          {dl_row}
        </div>
        '''

    # ① 📱 メッセージ・メール本文カード
    text_trans = post.get("text_translation") or (post.get("summary") if not post.get("image_translation") else "")
    text_raw = post.get("text_raw") or (post.get("source_text") if not post.get("image_raw") else "")
    text_card_html = ""
    if text_trans or text_raw:
        text_card_html = f'''
        <div class="p-4 rounded-2xl bg-amber-50/50 border border-amber-200/80 space-y-3">
          <h4 class="text-xs font-bold text-amber-900 flex items-center gap-1.5">
            <span>📱 メッセージ・メール本文の翻訳</span>
          </h4>
          <div class="text-xs leading-relaxed text-stone-800 bg-white p-3.5 rounded-xl border border-amber-200/50 whitespace-pre-wrap">{html.escape(str(text_trans or "本文翻訳なし"))}</div>
          {f"""<details class="text-xs pt-1">
            <summary class="font-bold text-amber-700 cursor-pointer hover:text-amber-950">🇺🇸 英語の原文テキストを表示</summary>
            <div class="mt-2 p-3 rounded-xl bg-white border border-stone-200 text-stone-600 text-[11px] font-mono whitespace-pre-wrap leading-relaxed">{html.escape(str(text_raw))}</div>
          </details>""" if text_raw else ""}
        </div>
        '''

    # ② 🖼️ 添付プリント写真 ＆ 画像内の翻訳カード
    img_url = post.get("image_url")
    img_trans = post.get("image_translation", "")
    img_raw = post.get("image_raw", "")
    image_card_html = ""
    if img_url or img_trans or img_raw:
        img_el = f'''
        <div class="w-full rounded-xl bg-white overflow-hidden border border-sky-200 flex items-center justify-center p-2">
          <img src="{img_url}" class="max-h-72 w-auto object-contain rounded-lg shadow-sm" alt="プリント">
        </div>
        ''' if img_url else ""

        trans_el = f'''
        <div class="text-xs leading-relaxed text-stone-800 bg-white p-3.5 rounded-xl border border-sky-200/50 whitespace-pre-wrap">{html.escape(str(img_trans))}</div>
        ''' if img_trans else ""

        raw_el = f'''
        <details class="text-xs pt-1">
          <summary class="font-bold text-sky-700 cursor-pointer hover:text-sky-950">🇺🇸 画像から読み取った英語原文 (OCR)</summary>
          <div class="mt-2 p-3 rounded-xl bg-white border border-stone-200 text-stone-600 text-[11px] font-mono whitespace-pre-wrap leading-relaxed">{html.escape(str(img_raw))}</div>
        </details>
        ''' if img_raw else ""

        image_card_html = f'''
        <div class="p-4 rounded-2xl bg-sky-50/50 border border-sky-200/80 space-y-3">
          <h4 class="text-xs font-bold text-sky-900 flex items-center gap-1.5">
            <span>🖼️ 添付プリント写真 ＆ 画像内の翻訳</span>
          </h4>
          {img_el}
          {trans_el}
          {raw_el}
        </div>
        '''

    # LINE共有文生成
    share_text = f"【おたより】{title}\n\n"
    if text_trans: share_text += f"📱 メッセージ:\n{text_trans}\n\n"
    if img_trans: share_text += f"🖼️ 添付プリント:\n{img_trans}\n\n"
    if items: share_text += f"🎒 持ち物: {', '.join(items)}\n"
    line_url = f"https://line.me/R/msg/text/?{urllib.parse.quote(share_text)}"

    # GoogleカレンダーURL生成
    cal_title = urllib.parse.quote(title)
    cal_loc = urllib.parse.quote(location)
    cal_desc = urllib.parse.quote(f"{title_en}\n\n{text_trans or img_trans}\n\n持ち物: {', '.join(items)}")
    d_clean = date_val.replace("-", "") if date_val else "20260907"
    cal_dates = f"{d_clean}/{d_clean}"
    google_cal_url = f"https://calendar.google.com/calendar/render?action=TEMPLATE&text={cal_title}&dates={cal_dates}&details={cal_desc}&location={cal_loc}"

    rendered = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{title} - School Info</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="/static/style.css?v=20260902_1435">
</head>
<body class="bg-stone-100 min-h-screen text-stone-800 antialiased flex justify-center py-0 sm:py-6">
  <div class="w-full max-w-lg bg-white min-h-screen sm:min-h-0 sm:rounded-3xl shadow-xl flex flex-col overflow-hidden">
    
    <!-- ヘッダー -->
    <header class="px-4 py-3.5 bg-white border-b border-stone-200/80 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      <a href="/" class="flex items-center gap-1.5 text-xs font-bold text-stone-600 hover:text-stone-900 bg-stone-100 hover:bg-stone-200 px-3 py-1.5 rounded-full transition">
        <span>← 一覧に戻る</span>
      </a>
      <div class="flex items-center gap-1.5">
        <a href="/edit/{post_id}" class="px-3 py-1.5 rounded-full bg-stone-100 hover:bg-stone-200 text-stone-700 font-bold text-xs shadow-sm flex items-center gap-1 transition">
          <span>✏️ 編集</span>
        </a>
        <a href="{line_url}" target="_blank" class="px-3 py-1.5 rounded-full bg-[#06C755] text-white font-bold text-xs shadow-sm flex items-center gap-1">
          <span>LINE共有</span>
        </a>
      </div>
    </header>

    <!-- コンテンツ -->
    <main class="p-5 space-y-4 flex-1">
      
      <!-- タイトル ＆ タグ -->
      <div class="space-y-2">
        <div class="flex flex-wrap gap-1.5 items-center">
          {tags_html}
          <span class="text-xs text-stone-400 font-semibold ml-auto">{date_display}</span>
        </div>
        <h1 class="text-xl font-black text-stone-900 leading-snug">{title}</h1>
        {f'<p class="text-xs text-stone-500 font-medium">{title_en}</p>' if title_en else ''}
      </div>

      <!-- 日時・場所 -->
      {datetime_html}

      <!-- 持ち物 -->
      {items_html}

      <!-- ① 📱 メッセージ・メール本文 -->
      {text_card_html}

      <!-- ② 🖼️ 添付プリント写真 ＆ 画像翻訳 -->
      {image_card_html}

      <!-- アクションボタン -->
      <div class="pt-3 grid grid-cols-2 gap-2.5">
        <a href="{google_cal_url}" target="_blank" class="py-3 px-3 rounded-2xl bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200 font-bold text-xs flex items-center justify-center gap-1.5 transition text-center shadow-sm">
          <span>📅 Googleカレンダーに追加</span>
        </a>
        <a href="{line_url}" target="_blank" class="py-3 px-3 rounded-2xl bg-[#06C755] text-white hover:bg-[#05b34c] font-bold text-xs flex items-center justify-center gap-1.5 transition text-center shadow-sm">
          <span>📲 LINEで家族に共有</span>
        </a>
      </div>

      <!-- 削除ボタン -->
      <div class="text-center pt-3 pb-2 border-t border-stone-100">
        <button onclick="deleteThisPost('{post_id}', '{title}')" class="text-xs font-bold text-red-500 hover:text-red-700 bg-red-50 hover:bg-red-100 border border-red-200 px-4 py-2.5 rounded-xl transition flex items-center justify-center gap-1.5 mx-auto active:scale-95">
          <span>🗑️ このおたよりを削除する</span>
        </button>
      </div>

      <!-- 戻るボタン -->
      <div class="text-center pt-2 pb-6">
        <a href="/" class="inline-block text-xs font-bold text-stone-500 hover:text-stone-800 bg-stone-100 px-5 py-2.5 rounded-2xl transition">
          ← おたより一覧に戻る
        </a>
      </div>

    </main>
  </div>

  <script>
    async function deleteThisPost(postId, postTitle) {{
      if (!confirm('「' + postTitle + '」を削除してもよろしいですか？')) return;
      try {{
        const res = await fetch('/api/posts/' + postId, {{ method: 'DELETE' }});
        if (res.ok) {{
          alert('🗑️ おたよりを削除しました');
          window.location.href = '/';
        }} else {{
          alert('削除に失敗しました');
        }}
      }} catch (err) {{
        alert('削除エラー: ' + err.message);
      }}
    }}
  </script>
</body>
</html>
'''
    return HTMLResponse(content=rendered, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    })

@app.get("/edit/{post_id}")
def get_edit_post_page(post_id: str):
    post = db.get_post_by_id(post_id)
    if not post:
        posts = db.get_all_posts()
        post = next((p for p in posts if str(p.get("id")) == str(post_id)), None)
    if not post:
        raise HTTPException(status_code=404, detail="おたよりが見つかりませんでした")

    title = html.escape(str(post.get("title") or ""))
    title_en = html.escape(str(post.get("title_en") or ""))
    text_trans = html.escape(str(post.get("text_translation") or (post.get("summary") if not post.get("image_translation") else "") or ""))
    text_raw = html.escape(str(post.get("text_raw") or (post.get("source_text") if not post.get("image_raw") else "") or ""))
    image_trans = html.escape(str(post.get("image_translation") or ""))
    image_raw = html.escape(str(post.get("image_raw") or ""))
    date_val = html.escape(str(post.get("date") or ""))
    time_start = html.escape(str(post.get("time_start") or ""))
    location = html.escape(str(post.get("location") or ""))
    deadline = html.escape(str(post.get("deadline") or ""))
    deadline_desc = html.escape(str(post.get("deadline_description") or ""))
    items_str = html.escape(", ".join(post.get("items") or []))
    image_url = html.escape(str(post.get("image_url") or ""))
    tags_json = json.dumps(post.get("tags") or ["英語・UOI"], ensure_ascii=False)

    image_preview_style = "" if image_url else "display: none;"

    edit_html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>おたよりを編集 - School Info</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="/static/style.css?v=20260903_1100">
</head>
<body class="bg-stone-100 min-h-screen text-stone-800 antialiased flex justify-center py-0 sm:py-6">
  <div class="w-full max-w-lg bg-white min-h-screen sm:min-h-0 sm:rounded-3xl shadow-xl flex flex-col overflow-hidden">
    
    <!-- ヘッダー -->
    <header class="px-4 py-3.5 bg-white border-b border-stone-200/80 flex items-center justify-between sticky top-0 z-30 shadow-sm">
      <a href="/post/{post_id}" class="flex items-center gap-1.5 text-xs font-bold text-stone-600 hover:text-stone-900 bg-stone-100 hover:bg-stone-200 px-3.5 py-2 rounded-full transition">
        <span>← キャンセル</span>
      </a>
      <h2 class="font-extrabold text-sm text-stone-800 flex items-center gap-1.5">
        <span>✏️ おたよりを編集</span>
      </h2>
      <div class="w-16"></div>
    </header>

    <!-- メインコンテンツ -->
    <main class="p-5 space-y-5 flex-1 overflow-y-auto">
      <form id="editForm" onsubmit="submitEdit(event)" class="space-y-5">

        <!-- 添付画像プレビュー ＆ 変更 -->
        <div class="p-3.5 bg-stone-50 rounded-2xl border border-stone-200 space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-stone-700">🖼️ 添付プリント写真</span>
            <button type="button" onclick="removeImage()" class="text-xs text-red-500 font-bold hover:underline">写真を削除</button>
          </div>
          
          <div id="imagePreviewBox" style="{image_preview_style}" class="w-full h-44 bg-white rounded-xl overflow-hidden flex items-center justify-center border border-stone-200">
            <img id="previewImageEl" src="{image_url}" class="w-full h-full object-contain" alt="添付写真">
          </div>

          <div class="pt-1">
            <input type="file" id="editFileInput" accept="image/*,application/pdf" class="hidden" onchange="handleEditFileChange(event)">
            <button type="button" onclick="document.getElementById('editFileInput').click()" class="w-full py-2.5 px-3 rounded-xl bg-white border border-stone-300 hover:bg-stone-100 text-xs font-bold text-stone-700 flex items-center justify-center gap-1.5 transition shadow-sm">
              <span>📷 写真を変更・再撮影する</span>
            </button>
            <p id="editFileStatus" class="hidden text-[11px] text-emerald-600 font-bold mt-1 text-center"></p>
          </div>
        </div>

        <!-- タイトル -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-stone-700 block">📌 タイトル（日本語） <span class="text-red-500">*</span></label>
          <input type="text" id="postTitle" required value="{title}" placeholder="例: 第1四半期のお知らせ（UOI評価タスク）"
                 class="w-full p-3 bg-stone-50 border border-stone-200 rounded-xl text-xs font-bold focus:outline-none focus:ring-2 focus:ring-emerald-400">
        </div>

        <!-- 英語原題 -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-stone-700 block">🇺🇸 英語の原題（タイトル）</label>
          <input type="text" id="postTitleEn" value="{title_en}" placeholder="例: Quarter 1, week 5 (Summative Assessment)"
                 class="w-full p-3 bg-stone-50 border border-stone-200 rounded-xl text-xs text-stone-600 focus:outline-none focus:ring-2 focus:ring-emerald-400">
        </div>

        <!-- ① 📱 メッセージ・メール本文翻訳 -->
        <div class="p-3.5 rounded-2xl bg-amber-50/60 border border-amber-200/80 space-y-2">
          <label class="text-xs font-bold text-amber-900 flex items-center gap-1">
            <span>📱 メッセージ・メール本文の翻訳（日本語）</span>
          </label>
          <textarea id="postTextTranslation" rows="4" placeholder="メール本文や連絡事項の日本語訳"
                    class="w-full p-3 text-xs bg-white border border-amber-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 leading-relaxed">{text_trans}</textarea>
          
          <details class="text-xs pt-1">
            <summary class="font-bold text-amber-800 cursor-pointer">🇺🇸 メッセージの英語原文</summary>
            <textarea id="postTextRaw" rows="3" placeholder="英語の本文原文"
                      class="mt-1.5 w-full p-2.5 text-[11px] bg-white border border-stone-200 rounded-xl font-mono text-stone-600">{text_raw}</textarea>
          </details>
        </div>

        <!-- ② 🖼️ 添付画像の翻訳 -->
        <div class="p-3.5 rounded-2xl bg-sky-50/60 border border-sky-200/80 space-y-2">
          <label class="text-xs font-bold text-sky-900 flex items-center gap-1">
            <span>🖼️ 添付プリント画像内の翻訳（日本語）</span>
          </label>
          <textarea id="postImageTranslation" rows="4" placeholder="プリント画像内に書かれている内容の日本語訳"
                    class="w-full p-3 text-xs bg-white border border-sky-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-400 leading-relaxed">{image_trans}</textarea>
          
          <details class="text-xs pt-1">
            <summary class="font-bold text-sky-800 cursor-pointer">🇺🇸 画像から読み取った英語原文 (OCR)</summary>
            <textarea id="postImageRaw" rows="3" placeholder="画像内OCR英語テキスト"
                      class="mt-1.5 w-full p-2.5 text-[11px] bg-white border border-stone-200 rounded-xl font-mono text-stone-600">{image_raw}</textarea>
          </details>
        </div>

        <!-- 日時・場所・締切 -->
        <div class="p-3.5 bg-stone-50 rounded-2xl border border-stone-200 space-y-3">
          <h4 class="text-xs font-bold text-stone-800">📅 日程 ＆ 場所</h4>
          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="text-[11px] text-stone-600 block mb-1">日付</label>
              <input type="date" id="postDate" value="{date_val}" class="w-full p-2 bg-white border border-stone-200 rounded-xl text-xs">
            </div>
            <div>
              <label class="text-[11px] text-stone-600 block mb-1">開始時間</label>
              <input type="time" id="postTimeStart" value="{time_start}" class="w-full p-2 bg-white border border-stone-200 rounded-xl text-xs">
            </div>
          </div>
          <div>
            <label class="text-[11px] text-stone-600 block mb-1">場所</label>
            <input type="text" id="postLocation" value="{location}" placeholder="学校 / 各教室など" class="w-full p-2 bg-white border border-stone-200 rounded-xl text-xs">
          </div>
          <div class="grid grid-cols-2 gap-2 border-t border-stone-200/60 pt-2">
            <div>
              <label class="text-[11px] text-red-600 font-bold block mb-1">⚠️ 提出締切日</label>
              <input type="date" id="postDeadline" value="{deadline}" class="w-full p-2 bg-white border border-red-200 rounded-xl text-xs">
            </div>
            <div>
              <label class="text-[11px] text-stone-600 block mb-1">提出物の内容</label>
              <input type="text" id="postDeadlineDesc" value="{deadline_desc}" placeholder="靴箱・写真など" class="w-full p-2 bg-white border border-stone-200 rounded-xl text-xs">
            </div>
          </div>
        </div>

        <!-- 持ち物リスト -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-stone-700 block">🎒 持ち物・持参するもの（カンマ区切り）</label>
          <input type="text" id="postItems" value="{items_str}" placeholder="靴箱, ステッカー, 写真, はさみ"
                 class="w-full p-3 bg-stone-50 border border-stone-200 rounded-xl text-xs focus:outline-none focus:ring-2 focus:ring-emerald-400">
        </div>

        <!-- タグ選択 -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-stone-700 block">🏷️ タグ</label>
          <div id="tagContainer" class="flex flex-wrap gap-1.5 pt-1"></div>
        </div>

        <!-- 保存ボタン -->
        <div class="pt-3 pb-8">
          <button type="submit" id="saveEditBtn" class="w-full py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-700 active:scale-[0.98] text-white font-black text-sm shadow-xl shadow-emerald-600/30 transition flex items-center justify-center gap-2">
            <span>💾 変更を保存する</span>
          </button>
        </div>

      </form>
    </main>
  </div>

  <script>
    const postId = "{post_id}";
    let currentUploadedImageUrl = "{image_url}";
    let selectedTags = {tags_json};
    const ALL_TAGS = ['英語・UOI', '中国語', 'アート', 'Music', '学校行事', '提出物あり'];

    function renderTags() {{
      const container = document.getElementById('tagContainer');
      container.innerHTML = ALL_TAGS.map(t => {{
        const isSel = selectedTags.includes(t);
        const bg = isSel ? 'bg-stone-800 text-white font-bold' : 'bg-stone-100 text-stone-600 hover:bg-stone-200';
        return `<button type="button" onclick="toggleTag('${{t}}')" class="px-3 py-1.5 rounded-full text-xs transition ${{bg}}">${{t}}</button>`;
      }}).join('');
    }}

    function toggleTag(t) {{
      if (selectedTags.includes(t)) {{
        selectedTags = selectedTags.filter(x => x !== t);
      }} else {{
        selectedTags.push(t);
      }}
      renderTags();
    }}

    async function handleEditFileChange(e) {{
      const file = e.target.files[0];
      if (!file) return;

      const statusEl = document.getElementById('editFileStatus');
      statusEl.innerText = '写真をアップロード中...';
      statusEl.classList.remove('hidden');

      const formData = new FormData();
      formData.append('file', file);

      try {{
        const res = await fetch('/api/upload', {{ method: 'POST', body: formData }});
        if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
        const data = await res.json();
        if (data.image_url) {{
          currentUploadedImageUrl = data.image_url;
          document.getElementById('previewImageEl').src = data.image_url;
          document.getElementById('imagePreviewBox').style.display = 'flex';
          statusEl.innerText = '✅ 写真を更新しました';
        }}
      }} catch (err) {{
        alert('写真のアップロードに失敗しました: ' + err.message);
        statusEl.innerText = '❌ 写真のアップロードに失敗しました';
      }}
    }}

    function removeImage() {{
      currentUploadedImageUrl = null;
      document.getElementById('imagePreviewBox').style.display = 'none';
      document.getElementById('previewImageEl').src = '';
      const statusEl = document.getElementById('editFileStatus');
      statusEl.innerText = '写真を削除しました';
      statusEl.classList.remove('hidden');
    }}

    async function submitEdit(e) {{
      e.preventDefault();
      const title = document.getElementById('postTitle').value.trim();
      if (!title) {{
        alert('タイトルを入力してください');
        return;
      }}

      const itemsStr = document.getElementById('postItems').value;
      const itemsArr = itemsStr ? itemsStr.split(',').map(s => s.trim()).filter(Boolean) : [];

      const updateData = {{
        title: title,
        title_en: document.getElementById('postTitleEn').value.trim() || null,
        text_translation: document.getElementById('postTextTranslation').value.trim() || null,
        text_raw: document.getElementById('postTextRaw').value.trim() || null,
        image_translation: document.getElementById('postImageTranslation').value.trim() || null,
        image_raw: document.getElementById('postImageRaw').value.trim() || null,
        summary: document.getElementById('postTextTranslation').value.trim() || document.getElementById('postImageTranslation').value.trim() || title,
        date: document.getElementById('postDate').value || null,
        time_start: document.getElementById('postTimeStart').value || null,
        location: document.getElementById('postLocation').value.trim() || null,
        deadline: document.getElementById('postDeadline').value || null,
        deadline_description: document.getElementById('postDeadlineDesc').value.trim() || null,
        items: itemsArr,
        tags: selectedTags,
        image_url: currentUploadedImageUrl
      }};

      try {{
        const btn = document.getElementById('saveEditBtn');
        btn.disabled = true;
        btn.innerText = '保存中...';

        const res = await fetch('/api/posts/' + postId, {{
          method: 'PUT',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(updateData)
        }});

        if (!res.ok) throw new Error(`HTTP ${{res.status}}`);
        
        // 詳細ページにリダイレクト
        window.location.href = '/post/' + postId;
      }} catch (err) {{
        alert('保存エラー: ' + err.message);
        document.getElementById('saveEditBtn').disabled = false;
        document.getElementById('saveEditBtn').innerText = '💾 変更を保存する';
      }}
    }}

    renderTags();
  </script>
</body>
</html>
'''
    return HTMLResponse(content=edit_html, headers={
        "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0"
    })

@app.post("/api/analyze")
async def analyze_document(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    英語おたより（画像/PDF/テキスト）を受け取り、AIで読取・日本語翻訳・構造化下書きを生成
    """
    image_bytes = None
    mime_type = "image/jpeg"
    image_url = None

    try:
        if file and file.filename:
            mime_type = file.content_type or "image/jpeg"
            content = await file.read()
            if len(content) > 0:
                image_bytes = content
                file_ext = os.path.splitext(file.filename)[1] or ".jpg"
                saved_filename = f"{uuid.uuid4()}{file_ext}"
                saved_path = os.path.join(UPLOAD_DIR, saved_filename)
                with open(saved_path, "wb") as f:
                    f.write(content)
                image_url = f"/uploads/{saved_filename}"

        settings = db.get_settings()
        api_key = settings.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")

        # AI解析＆翻訳の実行
        parsed_draft = ai_service.analyze_document(
            image_bytes=image_bytes,
            mime_type=mime_type,
            text_content=text,
            api_key=api_key
        )

        if image_url:
            parsed_draft["image_url"] = image_url

        return JSONResponse(content={
            "status": "success",
            "draft": parsed_draft
        })
    except Exception as e:
        print(f"[API Error /api/analyze]: {e}")
        # 万一のエラー時もフォールバックで返す
        fallback_draft = ai_service._intelligent_parse(None, text or "School Announcement")
        return JSONResponse(content={
            "status": "success",
            "draft": fallback_draft
        })

@app.post("/api/upload")
async def upload_image_only(file: UploadFile = File(...)):
    """おたより編集時などの画像単体アップロード"""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="ファイルが指定されていません")
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="空のファイルです")
    
    file_ext = os.path.splitext(file.filename)[1] or ".jpg"
    saved_filename = f"{uuid.uuid4()}{file_ext}"
    saved_path = os.path.join(UPLOAD_DIR, saved_filename)
    with open(saved_path, "wb") as f:
        f.write(content)
    
    image_url = f"/uploads/{saved_filename}"
    return {"status": "success", "image_url": image_url}

@app.get("/api/posts")
def get_posts(q: Optional[str] = Query(None), tag: Optional[str] = Query(None)):
    """おたより一覧取得・日英全文検索・タグフィルタ"""
    posts = db.get_all_posts(query=q, tag=tag)
    return {"posts": posts, "count": len(posts)}

@app.post("/api/posts")
def create_post(post: PostCreate):
    """確認・修正された下書きを保存"""
    data = post.dict()
    saved = db.add_post(data)
    return {"status": "success", "post": saved}

@app.get("/api/posts/{post_id}")
def get_post(post_id: str):
    post = db.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="おたよりが見つかりません")
    return post

@app.put("/api/posts/{post_id}")
def update_post(post_id: str, update_data: PostUpdate):
    data = {k: v for k, v in update_data.dict().items() if v is not None}
    updated = db.update_post(post_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="おたよりが見つかりません")
    return {"status": "success", "post": updated}

@app.delete("/api/posts/{post_id}")
def delete_post(post_id: str):
    deleted = db.delete_post(post_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="おたよりが見つかりません")
    return {"status": "success", "message": "削除しました"}

@app.get("/api/upcoming")
def get_upcoming():
    """直近の予定"""
    events = db.get_upcoming_events(limit=5)
    return {"events": events}

@app.get("/api/deadlines")
def get_deadlines():
    """提出物・締切アラート"""
    deadlines = db.get_pending_deadlines()
    return {"deadlines": deadlines}

@app.get("/api/settings")
def get_settings():
    settings = db.get_settings()
    # APIキーは末尾4桁以外マスクして返す
    masked_key = ""
    if settings.get("gemini_api_key"):
        raw = settings["gemini_api_key"]
        masked_key = f"{raw[:4]}...{raw[-4:]}" if len(raw) > 8 else "****"
    return {
        "user_name": settings.get("user_name", "yun"),
        "has_gemini_key": bool(settings.get("gemini_api_key")),
        "masked_gemini_key": masked_key,
        "notification_time": settings.get("notification_time", "18:00"),
        "line_configured": bool(settings.get("line_notify_token"))
    }

@app.post("/api/settings")
def update_settings(settings: SettingsUpdate):
    data = {k: v for k, v in settings.dict().items() if v is not None}
    updated = db.update_settings(data)
    return {"status": "success", "settings": updated}

@app.get("/api/calendar.ics")
def export_calendar(post_id: Optional[str] = None):
    """Googleカレンダー / iCal (.ics) ファイルの生成"""
    posts = [db.get_post_by_id(post_id)] if post_id else db.get_all_posts()
    posts = [p for p in posts if p and p.get("date")]

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Otayori Post//School Calendar//JA",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "X-WR-CALNAME:学校のおたより予定"
    ]

    for p in posts:
        event_date = p.get("date").replace("-", "")
        time_start = p.get("time_start", "08:30").replace(":", "") + "00"
        time_end = p.get("time_end", "15:00").replace(":", "") + "00"
        dtstart = f"{event_date}T{time_start}"
        dtend = f"{event_date}T{time_end}"

        items_str = ", ".join(p.get("items", []))
        summary = p.get("title", "学校行事")
        description = f"【内容】\\n{p.get('summary', '')}\\n\\n【持ち物】\\n{items_str}\\n\\n【英語原文タイトル】\\n{p.get('title_en', '')}"
        if p.get("deadline"):
            description += f"\\n\\n【提出締切】\\n{p.get('deadline')} ({p.get('deadline_description', '')})"

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{p.get('id')}@otayoripost.app",
            f"DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{dtstart}",
            f"DTEND:{dtend}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            f"LOCATION:{p.get('location', '学校')}",
            "END:VEVENT"
        ])

    lines.append("END:VCALENDAR")
    ics_content = "\r\n".join(lines)
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={"Content-Disposition": "attachment; filename=otayori_events.ics"}
    )

def _format_fairview_line_message(post: dict) -> str:
    title = post.get("title", "学校からのお知らせ")
    date_str = post.get("date", "")
    time_start = post.get("time_start", "")
    time_end = post.get("time_end", "")
    location = post.get("location", "")
    items = post.get("items", [])
    deadline = post.get("deadline", "")
    deadline_desc = post.get("deadline_description", "")
    summary = post.get("summary", "")

    lines = [
        "Fairview  school info📢",
        "🌟 重要な予定",
        f"📌「{title}」"
    ]

    details = []
    if date_str:
        t_str = f" ⏰ {time_start}〜{time_end}" if (time_start and time_end) else (f" ⏰ {time_start}" if time_start else "")
        details.append(f"📅 日程: {date_str.replace('-', '/')}{t_str}")
    text_trans = post.get("text_translation", "")
    img_trans = post.get("image_translation", "")
    summary = post.get("summary", "")

    if text_trans and img_trans:
        body_content = f"📱【メッセージ本文】\n{text_trans}\n\n🖼️【添付プリント翻訳】\n{img_trans}"
    elif img_trans and not text_trans:
        body_content = f"🖼️【添付プリント翻訳】\n{img_trans}"
    elif text_trans:
        body_content = f"{text_trans}"
    else:
        body_content = f"{summary}"

    lines.append("")
    lines.append("📝「本文」")
    lines.append(body_content)

    return "\n".join(lines)

@app.post("/api/line/notify")
def send_line_notification(req: LineNotifyRequest):
    """
    LINE通知シミュレーターおよび実送信 (絵文字リッチなFairview school info形式)
    """
    if req.custom_message:
        message = req.custom_message
    elif req.post_id:
        post = db.get_post_by_id(req.post_id)
        if not post:
            raise HTTPException(status_code=404, detail="おたよりが見つかりません")
        message = _format_fairview_line_message(post)
    else:
        upcoming = db.get_upcoming_events(limit=1)
        if upcoming:
            message = _format_fairview_line_message(upcoming[0])
        else:
            message = "Fairview  school info📢\n🌟 重要な予定\n📌「現在、特別な予定はありません」\n\n📝「本文」\n本日届いている緊急のおたよりはありません。良い一日を！😊✨"

    return {
        "status": "success",
        "message": message,
        "sent_at": datetime.now().strftime("%H:%M"),
        "channel": "LINE Messaging Preview"
    }

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import socket
    import time

    def find_free_port(start_port=8000, max_attempts=30):
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
                    return port
                except OSError:
                    continue
        return start_port

    target_port = find_free_port(8000)

    def open_browser(port):
        time.sleep(1.0)
        webbrowser.open(f"http://127.0.0.1:{port}")

    threading.Thread(target=open_browser, args=(target_port,), daemon=True).start()
    print(f"\n=======================================================")
    print(f"  おたよりポスト Webアプリを起動しました！")
    print(f"  PC用URL:     http://127.0.0.1:{target_port}")
    print(f"  スマホ用URL: http://192.168.100.161:{target_port} (同じWi-Fiから)")
    print(f"=======================================================\n")
    uvicorn.run("main:app", host="0.0.0.0", port=target_port, reload=False)
