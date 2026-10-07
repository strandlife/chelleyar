from datetime import date
from persiantools.jdatetime import JalaliDate
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