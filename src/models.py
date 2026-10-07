from dataclasses import dataclass, field
from datetime import date


@dataclass
class Cheleh:
    id: str
    name: str
    display_name: str
    task: str
    levels: list
    cycle_number: int = 1
    cycle_start_date: str = ""
    total_days: int = 40
    current_day: int = 1
    daily_logs: dict = field(default_factory=dict)
    history: list = field(default_factory=list)
    status: str = "active"  # "active" | "completed"

    def get_today_log(self, d: date | None = None) -> dict:
        key = str(self.current_day)
        if key not in self.daily_logs:
            self.daily_logs[key] = {
                "morning_note": "",
                "evening_note": "",
                "level_index": 0,
                "score": 0,
                "result": None,
                "morning_saved": False,
                "evening_saved": False,
                "date": (d or date.today()).isoformat(),
            }
        return self.daily_logs[key]

    def progress(self) -> int:
        return sum(1 for v in self.daily_logs.values()
                   if v.get("result") == "success")

    def is_last_day(self) -> bool:
        return self.current_day >= self.total_days

    def failure_level_index(self) -> int:
        """ایندکس سطح شکست در لیست سطوح"""
        for i, lv in enumerate(self.levels):
            if lv.get("score", 0) == 0:
                return i
        return -1