import flet as ft

from models import Chelleh
from database import Database
from navigation import NavigationMixin
from router import RouterMixin
from theme_manager import ThemeMixin
from chelleh_logic import ChellehLogicMixin


class ChellehApp(NavigationMixin, RouterMixin, ThemeMixin, ChellehLogicMixin):
    """هسته برنامه: نگه‌داری state، ذخیره‌سازی و مسیریابی.

    mixinها فقط متد می‌دهند؛ همه‌ی state اینجا تعریف می‌شود.
    """

    # حاشیه‌نویسی برای کمک به type-checker و خوانایی
    page: ft.Page
    db: Database
    chellehs: list[Chelleh]
    current_chelleh: Chelleh | None
    selected_day: str | None
    editing_chelleh: Chelleh | None
    theme_mode: str

    def __init__(self, page: ft.Page, db: Database):
        self.page = page
        self.db = db
        self.chellehs: list[Chelleh] = []
        self.selected_day = None
        self.editing_chelleh = None
        self.current_chelleh: Chelleh | None = None
        self.theme_mode = "light"

    # ----------------------------------------------------------------
    # چرخه حیات و داده
    # ----------------------------------------------------------------

    async def init(self):
        """بارگذاری داده‌ها از SharedPreferences"""
        self.chellehs = self.db.load_chellehs()
        saved = self.db.get_setting("theme_mode", "light")
        if saved in ("light", "dark", "system"):
            self.theme_mode = saved
        self.apply_theme()

    async def save(self):
        """ذخیره‌سازی داده‌ها"""
        for c in self.chellehs:
            self.db.save_chelleh(c)

    def snack(self, msg: str):
        """نمایش پیام موقت"""
        self.page.show_dialog(ft.SnackBar(ft.Text(msg)))