import json
import os
import uuid
from datetime import datetime, date
from typing import List, Dict, Any, Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

class Database:
    def __init__(self, filepath: str = DATA_FILE):
        self.filepath = filepath
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump({"posts": [], "settings": {
                    "user_name": "ゲスト",
                    "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
                    "line_notify_token": "",
                    "notification_time": "18:00"
                }}, f, ensure_ascii=False, indent=2)

    def _read_data(self) -> Dict[str, Any]:
        self._ensure_file()
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"posts": [], "settings": {}}

    def _write_data(self, data: Dict[str, Any]):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_settings(self) -> Dict[str, Any]:
        data = self._read_data()
        return data.get("settings", {})

    def update_settings(self, new_settings: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read_data()
        settings = data.get("settings", {})
        settings.update(new_settings)
        data["settings"] = settings
        self._write_data(data)
        return settings

    def get_all_posts(self, query: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._read_data()
        posts = data.get("posts", [])

        if tag and tag != "all":
            posts = [p for p in posts if tag in p.get("tags", [])]

        if query:
            q_lower = query.lower().strip()
            filtered = []
            for p in posts:
                # 日英全文検索（タイトル、英語タイトル、要約、英語原文、持ち物、タグ、日付）
                searchable_texts = [
                    p.get("title", ""),
                    p.get("title_en", ""),
                    p.get("summary", ""),
                    p.get("summary_en", ""),
                    p.get("source_text", ""),
                    p.get("date", ""),
                    p.get("deadline", ""),
                    " ".join(p.get("items", [])),
                    " ".join(p.get("tags", [])),
                    p.get("target_child", ""),
                    p.get("location", "")
                ]
                combined = " ".join(searchable_texts).lower()
                if q_lower in combined:
                    filtered.append(p)
            posts = filtered

        return posts

    def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        posts = self.get_all_posts()
        for p in posts:
            if p.get("id") == post_id:
                return p
        return None

    def add_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self._read_data()
        if "id" not in post_data or not post_data["id"]:
            post_data["id"] = str(uuid.uuid4())[:8]
        if "created_at" not in post_data:
            post_data["created_at"] = datetime.now().isoformat()
        
        # 既存チェック
        existing_idx = next((i for i, p in enumerate(data.get("posts", [])) if p.get("id") == post_data["id"]), None)
        if existing_idx is not None:
            data["posts"][existing_idx] = post_data
        else:
            data["posts"].insert(0, post_data)

        self._write_data(data)
        return post_data

    def update_post(self, post_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        data = self._read_data()
        for i, p in enumerate(data.get("posts", [])):
            if p.get("id") == post_id:
                p.update(update_data)
                p["updated_at"] = datetime.now().isoformat()
                data["posts"][i] = p
                self._write_data(data)
                return p
        return None

    def delete_post(self, post_id: str) -> bool:
        data = self._read_data()
        posts = data.get("posts", [])
        initial_len = len(posts)
        posts = [p for p in posts if p.get("id") != post_id]
        if len(posts) < initial_len:
            data["posts"] = posts
            self._write_data(data)
            return True
        return False

    def get_upcoming_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        """直近の予定（今日以降の日付があるもの）"""
        posts = self.get_all_posts()
        events = []
        for p in posts:
            p_date = p.get("date")
            if p_date:
                events.append(p)
        
        def sort_key(item):
            d = item.get("date", "9999-99-99")
            return d if d else "9999-99-99"

        events.sort(key=sort_key)
        return events[:limit]

    def get_pending_deadlines(self) -> List[Dict[str, Any]]:
        """締切（提出物）があるおたより"""
        posts = self.get_all_posts()
        deadlines = []
        for p in posts:
            if p.get("deadline") and not p.get("is_submitted", False):
                deadlines.append(p)
        
        deadlines.sort(key=lambda x: x.get("deadline", "9999-99-99"))
        return deadlines

db = Database()
