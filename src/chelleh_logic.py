from datetime import date

from models import Chelleh
from utils import get_unrecorded_days


class ChellehLogicMixin:
    """منطق دامنه‌ی چله: روزهای جامانده و شکست دوره"""

    def check_missed_days(self):
        """اولین چله فعالی که روز ثبت‌نشده دارد را پیدا و به صفحه تعیین تکلیف برو"""
        for ch in self.chellehs:
            if ch.status == "active" and get_unrecorded_days(ch):
                self.current_chelleh = ch
                self.navigate("/catchup")
                return

    def fail_chelleh(self, c: Chelleh):
        """شکست چله: بایگانی دوره فعلی و شروع دوره جدید از امروز"""
        today_iso = date.today().isoformat()
        c.history.append({
            "cycle": c.cycle_number,
            "status": "failed",
            "start_date": c.cycle_start_date,
            "end_date": today_iso,
            "days_completed": c.progress(),
        })
        c.cycle_number += 1
        c.cycle_start_date = today_iso
        c.current_day = 1
        c.daily_logs = {}
        c.status = "active"
        self.db.save_chelleh(c)