import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, Image as ReportLabImage
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
import pymupdf

# 日本語フォントの登録 (Meiryo & Meiryo Bold)
font_path_regular = r'C:\Windows\Fonts\meiryo.ttc'
font_path_bold = r'C:\Windows\Fonts\meiryob.ttc'

pdfmetrics.registerFont(TTFont('Meiryo', font_path_regular))
pdfmetrics.registerFont(TTFont('Meiryo-Bold', font_path_bold))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        # ヘッダー (2ページ目以降)
        if self._pageNumber > 1:
            self.setFont('Meiryo', 8)
            self.setFillColor(colors.HexColor('#78716C'))
            self.drawString(18 * mm, 285 * mm, "School Info ｜ 学校のおたより翻訳・予定管理アプリ 使い方ガイド")
            self.setStrokeColor(colors.HexColor('#E7E5E4'))
            self.setLineWidth(0.5)
            self.line(18 * mm, 282 * mm, 192 * mm, 282 * mm)

        # フッター (全ページ)
        self.setFont('Meiryo', 8)
        self.setFillColor(colors.HexColor('#78716C'))
        self.drawString(18 * mm, 12 * mm, "WebアプリURL: https://mmchan2525.github.io/schoolinfo/")
        page_str = f"Page {self._pageNumber} / {page_count}"
        self.drawRightString(192 * mm, 12 * mm, page_str)
        self.setStrokeColor(colors.HexColor('#E7E5E4'))
        self.setLineWidth(0.5)
        self.line(18 * mm, 15 * mm, 192 * mm, 15 * mm)
        self.restoreState()

def create_manual():
    output_pdf = "School_Info_User_Guide.pdf"
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    # カラーパレット (アプリのテーマカラーに統一)
    C_PRIMARY = colors.HexColor('#E11D48')       # ローズピンク
    C_PRIMARY_DARK = colors.HexColor('#9F1239')  # 濃いローズ
    C_SECONDARY = colors.HexColor('#D97706')     # アンバー
    C_SKY = colors.HexColor('#0284C7')           # スカイブルー
    C_EMERALD = colors.HexColor('#059669')       # エメラルドグリーン
    C_DARK = colors.HexColor('#1C1917')          # ダークストーン
    C_TEXT = colors.HexColor('#292524')          # 本文文字
    C_BG_CARD = colors.HexColor('#F8F5EE')       # アプリ背景
    C_BG_WHITE = colors.HexColor('#FFFFFF')
    C_BORDER = colors.HexColor('#E7E5E4')
    C_BORDER_LIGHT = colors.HexColor('#F5F5F4')

    styles = getSampleStyleSheet()

    # カスタムスタイル
    style_title = ParagraphStyle(
        'DocTitle',
        fontName='Meiryo-Bold',
        fontSize=18,
        leading=24,
        textColor=C_PRIMARY,
        spaceAfter=3
    )
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        fontName='Meiryo-Bold',
        fontSize=10.5,
        leading=15,
        textColor=C_DARK,
        spaceAfter=10
    )
    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        fontName='Meiryo-Bold',
        fontSize=11,
        leading=16,
        textColor=colors.white,
        spaceBefore=0,
        spaceAfter=0
    )
    style_body = ParagraphStyle(
        'Body_Custom',
        fontName='Meiryo',
        fontSize=8.2,
        leading=13,
        textColor=C_TEXT,
        spaceAfter=2
    )
    style_body_bold = ParagraphStyle(
        'Body_Bold_Custom',
        fontName='Meiryo-Bold',
        fontSize=8.2,
        leading=13,
        textColor=C_TEXT,
        spaceAfter=2
    )
    style_box_text = ParagraphStyle(
        'BoxText',
        fontName='Meiryo',
        fontSize=7.8,
        leading=12,
        textColor=C_TEXT
    )
    style_step_num = ParagraphStyle(
        'StepNum',
        fontName='Meiryo-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.white,
        alignment=1
    )

    story = []

    def section_header(title_text, bg_color=C_PRIMARY):
        p = Paragraph(f"<b>{title_text}</b>", style_h1)
        t = Table([[p]], colWidths=[178 * mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return t

    def info_box(title, text, bg=C_BG_CARD, border_color=C_PRIMARY, icon_label="【ポイント】"):
        content = [
            Paragraph(f"<b>{icon_label} {title}</b>", style_body_bold),
            Spacer(1, 1 * mm),
            Paragraph(text, style_box_text)
        ]
        t = Table([[content]], colWidths=[178 * mm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg),
            ('BOX', (0, 0), (-1, -1), 1, border_color),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        return t

    # ==========================================
    # PAGE 1: 表紙 ＆ はじめに・クイックスタート
    # ==========================================
    title_box = [
        Paragraph("School Info ｜ 取扱説明書 ＆ 活用マニュアル", style_title),
        Paragraph("学校・幼稚園のおたより翻訳＆予定管理 ｜ 作成者: <b>chan_meg</b> (otayori-translate v1.0)", style_subtitle)
    ]
    if os.path.exists("assets/avatar.jpg"):
        img_avatar = ReportLabImage("assets/avatar.jpg", width=16 * mm, height=16 * mm)
        t_title = Table([[img_avatar, title_box]], colWidths=[20 * mm, 158 * mm])
        t_title.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        story.append(t_title)
    else:
        story.append(title_box[0])
        story.append(title_box[1])
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_PRIMARY, spaceAfter=6, spaceBefore=3))

    story.append(section_header("1. アプリの概要 ＆ 主な特徴"))
    story.append(Spacer(1, 2 * mm))

    feature_table_data = [
        [
            Paragraph("<b>◆ 高精度AI翻訳 ＆ 要約</b>", style_body_bold),
            Paragraph("英語のプリントや連絡メールを、保護者向けに自然で丁寧な日本語に翻訳・要約します。表形式のスケジュールもセッションや日付ごとに自動で仕分け整理されます。", style_body)
        ],
        [
            Paragraph("<b>◆ 持ち物・日程・締切の自動抽出</b>", style_body_bold),
            Paragraph("おたよりの中から「持参するもの（靴箱、文具等）」「イベント日時・開始時刻」「提出締切日」をAIが自動検出し、カード上に目立つバッジで分かりやすく表示します。", style_body)
        ],
        [
            Paragraph("<b>◆ 写真の複数枚一括アップロード</b>", style_body_bold),
            Paragraph("複数ページにわたるプリントや、メール＋手紙をまとめて撮影・選択可能。複数枚を関連づけて1つのおたよりとしてAI解析・保存できます。", style_body)
        ],
        [
            Paragraph("<b>◆ お子さん別（兄弟姉妹）管理</b>", style_body_bold),
            Paragraph("お子さんごとに名前・性別・学年を設定し、タブでワンタップ切り替え。AIがおたよりの内容から対象のお子さんを自動判定して振り分けます。", style_body)
        ],
        [
            Paragraph("<b>◆ 直近の予定 自動アーカイブ</b>", style_body_bold),
            Paragraph("今日以降の直近イベントのみを上部にピックアップ表示。日程が過ぎた予定は自動で整理され、一覧アーカイブに保存されます。", style_body)
        ],
        [
            Paragraph("<b>◆ 安心の完全プライベート保存</b>", style_body_bold),
            Paragraph("おたよりや写真はお使いのスマホ・ブラウザ（LocalStorage）内に安全に保存され、外部サーバーに蓄積されません。", style_body)
        ]
    ]
    t_feat = Table(feature_table_data, colWidths=[52 * mm, 126 * mm])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAF9')),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 4 * mm))

    story.append(section_header("2. かんたん3ステップ！ クイックスタート", C_DARK))
    story.append(Spacer(1, 2 * mm))

    qs_data = [
        [
            Paragraph("<b>STEP 1</b>", style_step_num),
            Paragraph("<b>最初にお子さんを設定（画面右上の [設定] アイコン）</b><br/>画面右上の [設定] アイコンから、お子さんのお名前・性別（男の子/女の子）・年齢や学年を登録します（兄弟姉妹は何人でも登録可能）。", style_body)
        ],
        [
            Paragraph("<b>STEP 2</b>", style_step_num),
            Paragraph("<b>右下の「＋」ボタンでおたよりを追加</b><br/>プリントの写真をスマホで撮影（複数枚OK）するか、学校からの英語メール文章を貼り付けます。", style_body)
        ],
        [
            Paragraph("<b>STEP 3</b>", style_step_num),
            Paragraph("<b>「AIで読取」をタップして保存</b><br/>AIが数秒で日本語訳・持ち物・予定を整理。内容を確認して「保存」を押せば完了です！", style_body)
        ]
    ]
    t_qs = Table(qs_data, colWidths=[18 * mm, 160 * mm])
    t_qs.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), C_PRIMARY),
        ('BACKGROUND', (0, 1), (0, 1), C_SECONDARY),
        ('BACKGROUND', (0, 2), (0, 2), C_SKY),
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#FFFDF9')),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_qs)

    story.append(PageBreak())

    # ==========================================
    # PAGE 2: おたよりの登録 ＆ AI読取機能
    # ==========================================
    story.append(section_header("3. おたよりの登録手順（写真・テキスト）"))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("ホーム画面右下のピンクの <b>「＋」ボタン</b> をタップすると、新規おたより追加画面が開きます。", style_body))
    story.append(Spacer(1, 1 * mm))

    reg_steps = [
        [
            Paragraph("<b>① 写真の撮影 ＆ 複数選択</b>", style_body_bold),
            Paragraph("「写真を撮影 / プリント画像を選択」をタップするとカメラまたはアルバムが開きます。<br/>"
                      "・<b>複数枚の同時選択</b>: アルバムから2枚以上の写真をまとめて選択できます。<br/>"
                      "・<b>写真の追加撮影</b>: 1枚撮影した後、「＋ 写真を追加」を押して2枚目・3枚目を追加できます。<br/>"
                      "・<b>写真の削除</b>: 誤って選んだ写真はサムネイル右上の「×」で削除できます。<br/>"
                      "・<b>拡大プレビュー</b>: サムネイルをタップすると全画面ビューアで確認できます。<br/>"
                      "※ 写真は自動で軽量圧縮（約80〜150KB）されるため、スマホの容量を圧迫しません。", style_body)
        ],
        [
            Paragraph("<b>② 英語テキストの貼り付け</b>", style_body_bold),
            Paragraph("学校からの配信アプリ（ClassDojo, Seesaw, Google Classroom等）やメールの英文をコピーして貼り付けられます。（※写真のみ、テキストのみ、両方同時のいずれも対応）", style_body)
        ],
        [
            Paragraph("<b>③ AI読取 ＆ 翻訳開始</b>", style_body_bold),
            Paragraph("「<b>AIで読取 ＆ 日本語翻訳を開始</b>」ボタンをタップします。<br/>"
                      "・AIが写真内の英語文章や表を瞬時に解析し、分かりやすい日本語に変換します。<br/>"
                      "・複数枚の写真がある場合は、全ページを統合して1つのまとまったおたよりとして整理します。", style_body)
        ],
        [
            Paragraph("<b>④ 解析結果の確認 ＆ 編集</b>", style_body_bold),
            Paragraph("AIが抽出した以下の項目がフォームに自動入力されます。必要に応じて手動で微調整が可能です。<br/>"
                      "・<b>対象のお子さん</b>: 該当するお子さん（または全員共通）を選択<br/>"
                      "・<b>タイトル</b>: 日本語の分かりやすいタイトル<br/>"
                      "・<b>日本語訳 ＆ 連絡事項</b>: 日付やセッションごとに仕切り線が入った見やすい翻訳<br/>"
                      "・<b>持ち物リスト</b>: 持参するアイテム（カンマ区切りで複数設定可能）<br/>"
                      "・<b>日程 ＆ 時間 ＆ 場所</b>: イベントの開催日時<br/>"
                      "・<b>提出締切日 ＆ 内容</b>: 同意書や提出物の期限<br/>"
                      "・<b>タグ分類</b>: 教科やカテゴリ（English, Math, Mandarin, event, その他等）", style_body)
        ],
        [
            Paragraph("<b>⑤ 保存して完了</b>", style_body_bold),
            Paragraph("画面下の「<b>新しいおたよりを保存</b>」をタップすると登録が完了し、自動的に詳細画面へ移動します。", style_body)
        ]
    ]
    t_reg = Table(reg_steps, colWidths=[45 * mm, 133 * mm])
    t_reg.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFDF9')),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_reg)
    story.append(Spacer(1, 3 * mm))

    story.append(section_header("4. AI読取エンジン（2つのモード）について", C_SECONDARY))
    story.append(Spacer(1, 2 * mm))

    ai_mode_data = [
        [
            Paragraph("<b>◆ Gemini AI 高精度モード（無料・推奨）</b>", style_body_bold),
            Paragraph("Googleが提供する最先端AI（Gemini）が写真を直接解析します。手書き文字や複数列のスケジュール表、複雑なレイアウトも極めて正確に読み取り、自然な日本語に整理します。<br/>"
                      "※ ご自身のGoogle Gemini APIキー（無料）を設定画面に入力するだけで有効になります。", style_body)
        ],
        [
            Paragraph("<b>◆ 簡易OCR ＆ 翻訳モード（設定不要）</b>", style_body_bold),
            Paragraph("APIキーが未設定の場合でも、内蔵の高速OCRエンジンと学校専用辞書が自動でフォールバック動作し、基本的な英単語や持ち物・日付を読み取ります。", style_body)
        ]
    ]
    t_ai = Table(ai_mode_data, colWidths=[55 * mm, 123 * mm])
    t_ai.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAF9')),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_ai)

    story.append(PageBreak())

    # ==========================================
    # PAGE 3: ホーム画面 ＆ 詳細画面の便利機能
    # ==========================================
    story.append(section_header("5. ホーム画面の使い方 ＆ フィルタリング"))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("ホーム画面では、登録されたおたよりが目的別にすっきりと整理されて表示されます。", style_body))
    story.append(Spacer(1, 1 * mm))

    home_features = [
        [
            Paragraph("<b>◆ お子さん切り替えタブ</b>", style_body_bold),
            Paragraph("「全員」「たろう」「はなこ」などのタブをタップすると、そのお子さんに関係するおたよりだけを瞬時に絞り込み表示します。", style_body)
        ],
        [
            Paragraph("<b>◆ 直近の予定 エリア</b>", style_body_bold),
            Paragraph("今日以降に予定されているイベントが日付順（最大5件）でコンパクトに一覧表示されます。<br/>"
                      "・<b>消えるタイミング</b>: イベント当日が終わり、<b>翌日の午前0:00</b>を迎えると自動的に直近の予定から非表示になります。<br/>"
                      "・非表示後も下部の「届いたおたより一覧」には過去の履歴として大切に保管されます。", style_body)
        ],
        [
            Paragraph("<b>◆ 届いたおたより一覧</b>", style_body_bold),
            Paragraph("過去に登録したすべてのおたよりがカード形式で並びます。サムネイル画像、タイトル、要約文、持ち物バッジ、締切バッジなどがひと目で確認できます。<br/>"
                      "※ 複数写真があるおたよりには「写真 2枚」や「+1」の枚数バッジが付きます。", style_body)
        ],
        [
            Paragraph("<b>◆ タグフィルター</b>", style_body_bold),
            Paragraph("「すべて」「English」「Math」「Mandarin」「event」「提出物あり」などのチップをタップして、教科や種別ごとに一覧を絞り込めます。", style_body)
        ]
    ]
    t_home = Table(home_features, colWidths=[48 * mm, 130 * mm])
    t_home.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFDF9')),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_home)
    story.append(Spacer(1, 3 * mm))

    story.append(section_header("6. 詳細画面 ＆ 共有・連携機能", C_SKY))
    story.append(Spacer(1, 2 * mm))

    detail_features = [
        [
            Paragraph("<b>◆ 写真フォトギャラリー ＆ 拡大表示</b>", style_body_bold),
            Paragraph("登録された写真が一覧カードで表示されます。<b>写真をタップすると全画面の拡大ビューア（ライトボックス）</b>が開き、左右の矢印ボタンで高画質にプリントを閲覧できます。", style_body)
        ],
        [
            Paragraph("<b>◆ LINE共有ボタン</b>", style_body_bold),
            Paragraph("画面上部の「LINE共有」ボタンを押すと、おたよりのタイトル・日本語要約・持ち物リストが整ったテキストとしてLINE送信画面に自動セットされ、ご家族へワンタップでシェアできます。", style_body)
        ],
        [
            Paragraph("<b>◆ Googleカレンダー登録</b>", style_body_bold),
            Paragraph("「Googleカレンダーに追加」ボタンを押すと、おたよりの日時・タイトル・持ち物・詳細情報が入った予定登録画面がGoogleカレンダーで直接開きます。", style_body)
        ],
        [
            Paragraph("<b>◆ おたよりの編集 ＆ 削除</b>", style_body_bold),
            Paragraph("画面上部の「編集」から、文章の修正、写真の追加・削除、お子さんやタグの変更がいつでも行えます。不要になったおたよりは画面下部の「削除」で消去できます。", style_body)
        ]
    ]
    t_detail = Table(detail_features, colWidths=[52 * mm, 126 * mm])
    t_detail.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAF9')),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_detail)

    story.append(PageBreak())

    # ==========================================
    # PAGE 4: 設定画面 ＆ バックアップ ＆ スマホ活用
    # ==========================================
    story.append(section_header("7. 設定画面の機能 ＆ カスタマイズ"))
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("画面右上の <b>[設定] ボタン</b> から、アプリ全体の各種設定を行えます。", style_body))
    story.append(Spacer(1, 1 * mm))

    settings_data = [
        [
            Paragraph("<b>① ユーザー名設定</b>", style_body_bold),
            Paragraph("ホーム画面の「こんにちは、〇〇さん」に表示されるお名前を設定できます。", style_body)
        ],
        [
            Paragraph("<b>② お子さん設定（追加・並び替え・編集）</b>", style_body_bold),
            Paragraph("・<b>追加</b>: お名前、性別（男の子/女の子）、年齢・学年を入力して「＋ お子さんを追加」を押します。<br/>"
                      "・<b>並び替え</b>: 登録カードの「▲」「▼」ボタンでタブの並び順を自由に変更できます。<br/>"
                      "・<b>編集</b>: 「変更」ボタンを押すと、登録情報を修正できます。<br/>"
                      "・<b>削除</b>: 「×」ボタンで登録を解除できます。", style_body)
        ],
        [
            Paragraph("<b>③ タグの追加 ＆ 削除</b>", style_body_bold),
            Paragraph("標準タグ（English, Math, Mandarin, event, その他）を含め、すべてのタグを削除したり、新しいカスタムタグ（例: Science, 水泳, PTA, 提出物あり）を自由に追加できます。", style_body)
        ],
        [
            Paragraph("<b>④ Gemini APIキー設定</b>", style_body_bold),
            Paragraph("Google AI Studio (https://aistudio.google.com/app/apikey) で無料取得したAPIキーを入力すると、高精度OCR＆表組翻訳モードが有効になります。", style_body)
        ],
        [
            Paragraph("<b>⑤ データのバックアップ ＆ 復元</b>", style_body_bold),
            Paragraph("・<b>JSON保存</b>: 登録したすべてのおたより・お子さん設定をJSONファイルとして保存します。<br/>"
                      "・<b>復元</b>: 保存したJSONファイルを選択すると、別端末へデータをそのまま移行できます。<br/>"
                      "・<b>全削除・初期化</b>: すべてのデータをクリアして初期状態に戻します。", style_body)
        ],
        [
            Paragraph("<b>⑥ 最新版の読取 ＆ キャッシュクリア</b>", style_body_bold),
            Paragraph("「<b>最新版を読み込む</b>」ボタン（または画面右上の [更新] ボタン）を押すと、ブラウザキャッシュを完全クリアして最新の更新プログラムを再取得します。（※登録データは安全に保持されます）", style_body)
        ]
    ]
    t_set = Table(settings_data, colWidths=[48 * mm, 130 * mm])
    t_set.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFDF9')),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_set)
    story.append(Spacer(1, 2.5 * mm))

    story.append(section_header("8. スマートフォンでアプリのように使う方法（PWA）", C_DARK))
    story.append(Spacer(1, 1.5 * mm))

    pwa_data = [
        [
            Paragraph("<b>◆ iPhone (Safari)</b>", style_body_bold),
            Paragraph("① SafariでアプリURL（https://mmchan2525.github.io/schoolinfo/）を開きます。<br/>"
                      "② 画面下部中央の <b>共有アイコン（四角から上矢印）</b> をタップします。<br/>"
                      "③ メニューから <b>「ホーム画面に追加」</b> を選択します。<br/>"
                      "④ 右上の「追加」を押すとホーム画面に専用アイコンが追加され、全画面アプリとして起動できます。", style_body)
        ],
        [
            Paragraph("<b>◆ Android (Chrome)</b>", style_body_bold),
            Paragraph("① ChromeでアプリURLを開きます。<br/>"
                      "② 画面右上の <b>メニュー（縦の3点リーダー）</b> をタップします。<br/>"
                      "③ <b>「アプリをインストール」</b> または <b>「ホーム画面に追加」</b> を選択します。", style_body)
        ]
    ]
    t_pwa = Table(pwa_data, colWidths=[38 * mm, 140 * mm])
    t_pwa.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FAFAF9')),
        ('BOX', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_pwa)
    story.append(Spacer(1, 2.5 * mm))

    story.append(info_box(
        "最新の更新がスマホに反映されない場合（最新版を読み込むボタン）",
        "スマートフォンは通信量を抑えるために以前の画面を一時保存する性質があります。最新機能が画面に出ない場合は、画面右上の [更新] または設定画面の「最新版を読み込む」ボタンを一度タップしてください。",
        bg=colors.HexColor('#FEF3C7'),
        border_color=C_SECONDARY,
        icon_label="【ヒント】"
    ))

    # ドキュメント構築
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Manual successfully built at: {output_pdf}")

    # ページレンダリングテスト (PNG出力)
    doc_pymupdf = pymupdf.open(output_pdf)
    print(f"Verified PDF page count: {len(doc_pymupdf)}")
    for i, page in enumerate(doc_pymupdf):
        pix = page.get_pixmap(dpi=150)
        pix.save(f"manual_page_{i+1}.png")
    print("Exported page preview PNGs.")

if __name__ == '__main__':
    create_manual()
