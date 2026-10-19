import logging
from dataclasses import asdict, fields, MISSING
from datetime import datetime

from tinydb import TinyDB, Query

from models import Chelleh

logger = logging.getLogger(__name__)

DB_PATH = "cheleh_yar_db.json"


def _clean_for_model(model_cls, item: dict) -> dict:
    """فیلدهای ناشناخته را حذف، None ها را با پیش‌فرض پر و فیلدهای ضروری را بررسی می‌کند."""
    all_fields = fields(model_cls)
    valid = {f.name for f in all_fields}
    cleaned = {k: v for k, v in item.items() if k in valid}

    # مقادیر None (معمول در بک‌آپ‌های قدیمی) با پیش‌فرض فیلد جایگزین شوند
    for f in all_fields:
        if cleaned.get(f.name) is None:
            if f.default is not MISSING:
                cleaned[f.name] = f.default
            elif f.default_factory is not MISSING:
                cleaned[f.name] = f.default_factory()

    # سازگاری با نام قدیمی فیلد
    if not cleaned.get("cycle_start_date"):
        cleaned["cycle_start_date"] = item.get("start_date", "")

    # فیلدهای بدون پیش‌فرض (id, name, display_name, task, levels) باید باشند
    required = {f.name for f in all_fields
                if f.default is MISSING and f.default_factory is MISSING}
    missing = [r for r in required if cleaned.get(r) is None]
    if missing:
        raise ValueError(f"فیلدهای ضروری ناقص: {missing}")

    return cleaned


def _to_model(item: dict) -> Chelleh:
    """ساخت مدل از رکورد خام دیتابیس (با پاک‌سازی)."""
    return Chelleh(**_clean_for_model(Chelleh, item))


class Database:
    def __init__(self, path: str = DB_PATH):
        self.db = TinyDB(path, indent=2, ensure_ascii=False)
        self.chellehs_table = self.db.table("chellehs")
        self.settings_table = self.db.table("settings")
        self.Query = Query()

    # ---------- settings ----------
    def get_setting(self, key: str, default=None):
        result = self.settings_table.search(self.Query.key == key)
        return result[0]["value"] if result else default

    def set_setting(self, key: str, value):
        self.settings_table.upsert({"key": key, "value": value},
                                   self.Query.key == key)

    # ---------- chellehs ----------
    def load_chellehs(self) -> list[Chelleh]:
        models = []
        for item in self.chellehs_table.all():
            try:
                models.append(_to_model(item))
            except Exception as e:
                logger.warning("رکورد خراب نادیده گرفته شد: %s", e)
        return models

    def get_chelleh(self, chelleh_id: str) -> Chelleh | None:
        result = self.chellehs_table.search(self.Query.id == chelleh_id)
        if not result:
            return None
        try:
            return _to_model(result[0])
        except Exception as e:
            logger.warning("چله‌ی خراب (%s): %s", chelleh_id, e)
            return None

    def save_chelleh(self, chelleh: Chelleh):
        data = asdict(chelleh)
        self.chellehs_table.upsert(data, self.Query.id == chelleh.id)

    def delete_chelleh(self, chelleh_id: str):
        self.chellehs_table.remove(self.Query.id == chelleh_id)

    # ---------- بک‌آپ و بازیابی ----------
    def export_all(self) -> dict:
        return {
            "version": 1,
            "app": "cheleh_yar",
            "exported_at": datetime.now().isoformat(),
            "chellehs": self.chellehs_table.all(),
            "settings": self.settings_table.all(),
        }

    def import_all(self, data: dict, replace: bool = False) -> tuple[int, int]:
        """ورود داده‌ها از فایل بک‌آپ.

        replace=True  -> پس از اعتبارسنجیِ موفق همه‌ی موارد، داده‌های فعلی جایگزین می‌شوند
        replace=False -> بدون تکرار id اضافه می‌شوند

        Returns:
            (تعداد چله‌های اضافه‌شده, تعداد رد شده)
        """
        if not isinstance(data, dict):
            raise ValueError("ساختار فایل بک‌آپ نامعتبر است")
        if data.get("app") != "cheleh_yar":
            raise ValueError("این فایل مربوط به برنامه «چله‌یار» نیست")

        incoming = data.get("chellehs")
        if not isinstance(incoming, list):
            raise ValueError("بخش چله‌ها در فایل بک‌آپ نامعتبر است")

        # مرحله ۱: اعتبارسنجی و پاک‌سازی همه‌ی موارد (دیتابیس هنوز دست نخورده)
        existing_ids = set() if replace else {
            i.get("id") for i in self.chellehs_table.all()
        }
        valid_items, skipped = [], 0
        for item in incoming:
            if not isinstance(item, dict):
                skipped += 1
                continue
            try:
                cleaned = _clean_for_model(Chelleh, item)
                Chelleh(**cleaned)  # اعتبارسنجی نهایی
            except Exception:
                skipped += 1
                continue
            cid = cleaned.get("id")
            if cid and cid in existing_ids:
                skipped += 1
                continue
            valid_items.append(cleaned)
            if cid:
                existing_ids.add(cid)

        # مرحله ۲: حالا که همه‌چیز سالم است، دیتابیس به‌روزرسانی می‌شود
        if replace:
            self.chellehs_table.truncate()
            self.settings_table.truncate()
        for cleaned in valid_items:
            self.chellehs_table.upsert(cleaned, self.Query.id == cleaned["id"])

        # تنظیمات (فقط کلیدهای جدید)
        for s in (data.get("settings") or []):
            if not isinstance(s, dict) or s.get("key") is None:
                continue
            if not self.settings_table.search(self.Query.key == s["key"]):
                self.settings_table.insert(s)

        return len(valid_items), skipped

    # ---------- متفرقه ----------
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        self.db.close()