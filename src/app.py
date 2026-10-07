import flet as ft
from models import Cheleh
from theme import make_appbar
from database import Database
from views.list_view import build_list_view
from views.day_detail_view import build_day_detail_view
from views.add_view import build_add_view
from views.status_view import build_status_view
from views.edit_view import build_edit_view   # ← اضافه کنید
from views.stats_view import build_stats_view
from views.about_view import build_about_view


THEME_KEY = "cheleh_yar_theme_mode"



class ChelehApp:
    """هسته برنامه: نگه‌داری state، ذخیره‌سازی و مسیریابی"""

    def __init__(self, page: ft.Page, db: Database):
        self.page = page
        self.db = db
        self.chelehs: list[Cheleh] = []
        self.selected_day = None          # ← جدید
        self.editing_cheleh = None      # ← اضافه کنید
        self.current_cheleh: Cheleh | None = None
        self.theme_mode = "light"

    async def init(self):
        """بارگذاری داده‌ها از SharedPreferences"""
        self.chelehs = self.db.load_chelehs()
        # self.chelehs = await load_chelehs(self.prefs)
        saved = self.db.get_setting("theme_mode", "light")
        if saved in ("light", "dark", "system"):
            self.theme_mode = saved
        self.apply_theme()

    def open_edit(self, ch):
        """رفتن به صفحه ویرایش چله"""
        self.editing_cheleh = ch
        self.navigate("/edit")

    def open_stats(self, ch):
        """رفتن به صفحه آمار برای یک چله"""
        self.current_cheleh = ch
        self.navigate("/stats")

    async def save(self):
        """ذخیره‌سازی داده‌ها"""
        # await save_chelehs(self.prefs, self.chelehs)
        for c in self.chelehs:
            self.db.save_cheleh(c)

    def snack(self, msg: str):
        """نمایش پیام موقت"""
        self.page.show_dialog(ft.SnackBar(ft.Text(msg)))

    def navigate(self, route: str):
        """ناوبری به مسیر مشخص"""
        self.page.run_task(self.page.push_route, route)

    def refresh(self):
        """بازسازی صفحه فعلی بدون تغییر تاریخچه"""
        self.route_change(None)

    def open_status(self, ch: Cheleh):
        """رفتن به صفحه وضعیت یک چله"""
        self.current_cheleh = ch
        self.navigate("/status")

    def route_change(self, e):
        page = self.page
        page.views.clear()
        route = page.route or "/"

        if route == "/add":
            page.views.append(ft.View(
                route="/add",
                appbar=make_appbar(
                    title="افزودن چله جدید",
                    subtitle="یک مسیر تازه ۴۰ روزه",
                    show_back=True,
                    on_back=lambda e: self.navigate("/"),
                ),
                controls=[build_add_view(self)],
            ))
        elif route == "/edit":
            subtitle = (self.editing_cheleh.display_name
                if self.editing_cheleh else "")
            page.views.append(ft.View(
                route="/edit",
                appbar=make_appbar(
                    title="ویرایش چله",
                    subtitle=subtitle,
                    show_back=True,
                    on_back=lambda e: self.navigate("/"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_edit_view(self)],
            ))
        elif route == "/day":
            subtitle = ""
            if self.current_cheleh and self.selected_day:
                subtitle = f"روز {self.selected_day}"
            page.views.append(ft.View(
                route="/day",
                appbar=make_appbar(
                    title="جزئیات روز",
                    subtitle=subtitle,
                    show_back=True,
                    on_back=lambda e: self.navigate("/status"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_day_detail_view(self)],
            ))
        elif route == "/status":
            subtitle = (self.current_cheleh.display_name
                if self.current_cheleh else "")
            page.views.append(ft.View(
                route="/status",
                appbar=make_appbar(
                    title="وضعیت چله",
                    subtitle=subtitle,
                    show_back=True,
                    on_back=lambda e: self.navigate("/"),
                    actions=[
                        ft.IconButton(
                            ft.Icons.INSIGHTS_OUTLINED,
                            tooltip="آمار",
                            on_click=lambda e: self.navigate("/stats"),
                        ),
                    ],
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_status_view(self)],
            ))
        elif route == "/stats":
            subtitle = (self.current_cheleh.display_name
                if self.current_cheleh else "")
            page.views.append(ft.View(
                route="/stats",
                appbar=make_appbar(
                    title="آمار و گزارش",
                    subtitle=subtitle,
                    show_back=True,
                    on_back=lambda e: self.navigate("/status"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_stats_view(self)],
            ))
        elif route == "/about":
            page.views.append(ft.View(
                route="/about",
                appbar=make_appbar(
                    title="درباره برنامه",
                    show_back=True,
                    on_back=lambda e: self.navigate("/"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_about_view(self)],
            ))
        else:
            theme_icon = (ft.Icons.DARK_MODE if self.theme_mode == "light"
                  else ft.Icons.LIGHT_MODE)
            page.views.append(ft.View(
                route="/",
                appbar=make_appbar(
                    title="چله‌یار",
                    actions=[
                        ft.IconButton(
                            theme_icon,
                            tooltip="حالت شب/روز",
                            on_click=lambda e: page.run_task(self.toggle_theme),
                        ),
                        ft.IconButton(
                            ft.Icons.INFO_OUTLINE,
                            tooltip="درباره",
                            on_click=lambda e: self.navigate("/about"),
                        ),
                    ],
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    build_list_view(self),
                ],
                floating_action_button=ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    tooltip="افزودن چله",
                    on_click=lambda e: self.navigate("/add"),
                ),
            ))
        page.update()

    def apply_theme(self):
        """اعمال حالت شب روی page"""
        mapping = {
            "light": ft.ThemeMode.LIGHT,
            "dark": ft.ThemeMode.DARK,
            "system": ft.ThemeMode.SYSTEM,
        }
        self.page.theme_mode = mapping.get(self.theme_mode, ft.ThemeMode.LIGHT)
        self.page.update()

    async def toggle_theme(self):
        """تغییر بین حالت روشن و تاریک"""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.db.set_setting("theme_mode", self.theme_mode)
        self.apply_theme()
        self.refresh() 