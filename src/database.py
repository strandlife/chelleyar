from tinydb import TinyDB, Query
from dataclasses import asdict
from models import Cheleh

DB_PATH = "cheleh_yar_db.json"


class Database:
    def __init__(self, path: str = DB_PATH):
        self.db = TinyDB(path, indent=2, ensure_ascii=False)
        self.chelehs_table = self.db.table("chelehs")
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

    def load_chelehs(self) -> list[Cheleh]:
        raw = self.chelehs_table.all()
        return [Cheleh(**item) for item in raw]

    def save_cheleh(self, cheleh: Cheleh):
        data = asdict(cheleh)
        self.chelehs_table.upsert(data, self.Query.id == cheleh.id)

    def delete_cheleh(self, cheleh_id: str):
        self.chelehs_table.remove(self.Query.id == cheleh_id)

    def get_cheleh(self, cheleh_id: str) -> Cheleh | None:
        result = self.chelehs_table.search(self.Query.id == cheleh_id)
        return Cheleh(**result[0]) if result else None

    def close(self):
        self.db.close()