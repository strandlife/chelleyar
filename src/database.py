from tinydb import TinyDB, Query
from dataclasses import asdict
from models import Chelleh

DB_PATH = "cheleh_yar_db.json"


def _clean_for_model(model_cls, item: dict) -> dict:
    """فیلدهای ناشناخته را حذف و فیلدهای ضروری را پر می‌کند."""
    from dataclasses import fields
    valid = {f.name for f in fields(model_cls)}
    cleaned = {k: v for k, v in item.items() if k in valid}
    # مقادیر پیش‌فرض برای فیلدهای جدید
    cleaned.setdefault("cycle_number", 1)
    cleaned.setdefault("cycle_start_date", item.get("start_date", ""))
    cleaned.setdefault("total_days", 40)
    cleaned.setdefault("current_day", 1)
    cleaned.setdefault("daily_logs", {})
    cleaned.setdefault("history", [])
    cleaned.setdefault("status", "active")
    return cleaned


class Database:
    def __init__(self, path: str = DB_PATH):
        self.db = TinyDB(path, indent=2, ensure_ascii=False)
        self.chellehs_table = self.db.table("chellehs")
        self.settings_table = self.db.table("settings")
        self.Query = Query()

    def get_setting(self, key: str, default=None):
        result = self.settings_table.search(self.Query.key == key)
        return result[0]["value"] if result else default

    def set_setting(self, key: str, value):
        self.settings_table.upsert(
            {"key": key, "value": value},
            self.Query.key == key,
        )

    def load_chellehs(self) -> list[Chelleh]:
        raw = self.chellehs_table.all()
        return [Chelleh(**item) for item in raw]

    def save_chelleh(self, chelleh: Chelleh):
        data = asdict(chelleh)
        self.chellehs_table.upsert(data, self.Query.id == chelleh.id)

    def delete_chelleh(self, chelleh_id: str):
        self.chellehs_table.remove(self.Query.id == chelleh_id)

    def get_chelleh(self, chelleh_id: str) -> Chelleh | None:
        result = self.chellehs_table.search(self.Query.id == chelleh_id)
        return Chelleh(**result[0]) if result else None

    def export_all(self) -> dict:
        """خروجی کامل از کل پایگاه داده برای بک‌آپ"""
        return {
            "version": 1,
            "app": "cheleh_yar",
            "exported_at": __import__("datetime").datetime.now().isoformat(),
            "chellehs": self.chellehs_table.all(),
            "settings": self.settings_table.all(),
        }

    def import_all(self, data: dict, replace: bool = False) -> tuple[int, int]:
        """ورود داده‌ها از فایل بک‌آپ.

        replace=True  → داده‌های فعلی پاک و با داده‌های فایل جایگزین می‌شوند
        replace=False → داده‌ها به داده‌های موجود اضافه می‌شوند (بدون تکرار id)

        Returns:
            (تعداد چله‌های اضافه‌شده, تعداد چله‌های رد شده)
        """
        if not isinstance(data, dict):
            raise ValueError("ساختار فایل بک‌آپ نامعتبر است")

        if data.get("app") != "cheleh_yar":
            raise ValueError("این فایل مربوط به برنامه «چله‌یار» نیست")

        incoming_chellehs = data.get("chellehs")
        if not isinstance(incoming_chellehs, list):
            raise ValueError("بخش چله‌ها در فایل بک‌آپ نامعتبر است")

        if replace:
            self.chellehs_table.truncate()
            self.settings_table.truncate()

        # شناسه‌های موجود برای جلوگیری از تکرار
        existing_ids = {item.get("id") for item in self.chellehs_table.all()}

        added = 0
        skipped = 0
        for item in incoming_chellehs:
            if not isinstance(item, dict):
                skipped += 1
                continue
            cid = item.get("id")
            if cid and cid in existing_ids:
                skipped += 1
                continue
            # تلاش برای ساخت مدل معتبر قبل از درج
            try:
                from models import Chelleh
                Chelleh(**_clean_for_model(Chelleh, item))
            except Exception:
                skipped += 1
                continue
            self.chellehs_table.insert(item)
            if cid:
                existing_ids.add(cid)
            added += 1

        # تنظیمات (فقط اگر replace یا کلید جدید بود)
        incoming_settings = data.get("settings") or []
        if isinstance(incoming_settings, list):
            for s in incoming_settings:
                if not isinstance(s, dict):
                    continue
                key = s.get("key")
                if key is None:
                    continue
                existing = self.settings_table.search(self.Query.key == key)
                if not existing:
                    self.settings_table.insert(s)

        return added, skipped
    def close(self):
        self.db.close()