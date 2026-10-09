from datetime import date
from persiantools.jdatetime import JalaliDate
from datetime import date, timedelta
import flet as ft


COLOR_OPTIONS = [
    ("#2E7D32", "سبز تیره"),
    ("#4CAF50", "سبز چمنی"),
    ("#8BC34A", "سبز روشن"),
    ("#1976D2", "آبی"),
    ("#0288D1", "آبی روشن"),
    ("#F57C00", "نارنجی"),
    ("#D32F2F", "قرمز"),
    ("#7B1FA2", "بنفش"),
    ("#5D4037", "قهوه‌ای"),
    ("#455A64", "خاکستری"),
]



def from_jalali(jalali_str: str) -> date:
    """تبدیل رشته شمسی (YYYY/MM/DD) به date میلادی"""
    y, m, d = map(int, jalali_str.split("/"))
    return JalaliDate(y, m, d).to_gregorian()

def to_jalali(d: date) -> str:
    """تبدیل تاریخ میلادی به شمسی (YYYY/MM/DD)"""
    return JalaliDate(d).strftime("%Y/%m/%d")


def readable_text_color(hex_color: str) -> str:
    """انتخاب رنگ متن مناسب (سیاه/سفید) بر اساس روشنایی پس‌زمینه"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return ft.Colors.WHITE
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return ft.Colors.BLACK if lum > 140 else ft.Colors.WHITE


_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")

def to_persian_digits(s: str) -> str:
    """اعداد لاتین رشته را به اعداد فارسی تبدیل می‌کند"""
    return s.translate(_PERSIAN_DIGITS)

def compute_current_day(c, today: date | None = None) -> int:
    """شماره روز امروز را از روی تاریخ شروع محاسبه می‌کند (نه مقدار ذخیره‌شده).
    صفر یعنی چله هنوز شروع نشده."""
    if today is None:
        today = date.today()
    start = date.fromisoformat(c.cycle_start_date)
    diff = (today - start).days + 1   # خودِ روز شروع = روز ۱
    return min(max(diff, 0), c.total_days)


def get_unrecorded_days(c, today: date | None = None) -> list[int]:
    """روزهای سپری‌شده‌ای که هنوز نتیجه‌ای برایشان ثبت نشده است."""
    if c is None or c.status != "active":
        return []
    current = compute_current_day(c, today)
    return [
        i for i in range(1, current)          # برای حذف «امروز»: range(1, current)
        if not c.daily_logs.get(str(i), {}).get("result")
    ]