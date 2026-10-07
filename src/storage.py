import json
from dataclasses import asdict
from models import Cheleh


STORAGE_KEY = "cheleh_yar_data_v1"


async def load_chelehs(prefs) -> list[Cheleh]:
    raw = await prefs.get(STORAGE_KEY)
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return [Cheleh(**c) for c in data]
    except Exception:
        return []


async def save_chelehs(prefs, chelehs: list[Cheleh]) -> None:
    await prefs.set(
        STORAGE_KEY,
        json.dumps([asdict(c) for c in chelehs], ensure_ascii=False),
    )