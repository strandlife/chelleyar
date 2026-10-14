from tinydb import TinyDB, Query
from dataclasses import asdict
from models import Chelleh

DB_PATH = "cheleh_yar_db.json"


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

    def close(self):
        self.db.close()