import flet as ft
from models import Cheleh
from datetime import date
from utils import get_unrecorded_days
from theme import make_appbar, import_cheleh_action
from database import Database
from views.list_view import build_list_view
from views.day_detail_view import build_day_detail_view
from views.add_view import build_add_view
from views.status_view import build_status_view
from views.edit_view import build_edit_view
from views.stats_view import build_stats_view
from views.catchup_view import build_catchup_view
from views.about_view import build_about_view
from views.science_view import build_science_view


THEME_KEY = "cheleh_yar_theme_mode"

# ==================================================================
# ناوبری — طبق مدل مسیریابی فلت
# استک ویوهای هر مسیر: همیشه از ریشه (/) تا خودِ مسیر
# ==================================================================

NAV_STACKS = {
    "/":        ["/"],
    "/add":     ["/", "/add"],
    "/edit":    ["/", "/edit"],
    "/about":   ["/", "/about"],
    "/status":  ["/", "/status"],
    "/science":  ["/", "/science"],
    "/stats":   ["/", "/status", "/stats"],
    "/day":     ["/", "/status", "/day"],
    "/catchup": ["/", "/status", "/catchup"],
}

# مسیرهایی که برای ساخته‌شدن به current_cheleh نیاز دارند
CHELEH_ROUTES = ("/status", "/stats", "/day", "/catchup")


class ChelehApp:
    """هسته برنامه: نگه‌داری state، ذخیره‌سازی و مسیریابی"""

    def __init__(self, page: ft.Page, db: Database):
        self.page = page
        self.db = db
        self.chelehs: list[Cheleh] = []
        self.selected_day = None
        self.editing_cheleh = None
        self.current_cheleh: Cheleh | None = None
        self.theme_mode = "light"

    # ----------------------------------------------------------------
    # چرخه حیات و داده
    # ----------------------------------------------------------------

    async def init(self):
        """بارگذاری داده‌ها از SharedPreferences"""
        self.chelehs = self.db.load_chelehs()
        saved = self.db.get_setting("theme_mode", "light")
        if saved in ("light", "dark", "system"):
            self.theme_mode = saved
        self.apply_theme()

    async def save(self):
        """ذخیره‌سازی داده‌ها"""
        for c in self.chelehs:
            self.db.save_cheleh(c)

    def snack(self, msg: str):
        """نمایش پیام موقت"""
        self.page.show_dialog(ft.SnackBar(ft.Text(msg)))

    # ----------------------------------------------------------------
    # ناوبری
    # ----------------------------------------------------------------

    def navigate(self, route: str):
        """ناوبری به جلو از کال‌بک‌های sync — طبق مستندات فلت"""
        self.page.navigate(route)

    def go_back(self, target: str = "/"):
        """برگشت به مقصد — حذف ویوهای روی استک تا مقصد.

        اگر مستقیماً به‌عنوان هندلر رویداد صدا زده شود، آرگومان
        event خواهد بود؛ در آن صورت به ریشه برمی‌گردیم.
        """
        if not isinstance(target, str):
            target = "/"
        if (self.page.route or "/") == target:
            return
        pop_until = getattr(self.page, "pop_views_until", None)
        if pop_until is not None:
            self.page.run_task(pop_until, target)
        else:  # نسخه‌های قدیمی‌تر فلت
            self.page.run_task(self.page.push_route, target)

    async def view_pop(self, e: ft.ViewPopEvent):
        """Back سیستم / مرورگر — الگوی رسمی مستندات"""
        page = self.page
        if e.view is not None and e.view in page.views:
            page.views.remove(e.view)
        if not page.views:
            await page.push_route("/")
            return
        top = page.views[-1]
        if (page.route or "/") != top.route:
            await page.push_route(top.route)

    def refresh(self):
        """بازسازی صفحه فعلی بدون تغییر تاریخچه"""
        self.route_change(None)

    def open_edit(self, ch):
        """رفتن به صفحه ویرایش چله"""
        self.editing_cheleh = ch
        self.navigate("/edit")

    def open_stats(self, ch):
        """رفتن به صفحه آمار برای یک چله"""
        self.current_cheleh = ch
        self.navigate("/stats")

    def open_status(self, ch: Cheleh):
        """رفتن به صفحه وضعیت یک چله"""
        self.current_cheleh = ch
        self.navigate("/status")

    # ----------------------------------------------------------------
    # مسیریابی — استک ویوها از route مشتق می‌شود (single source of truth)
    # ----------------------------------------------------------------

    def _stack_for_route(self, route: str) -> list[str]:
        """استک ویوهای معتبر برای مسیر فعلی + محافظ deep-link/reload."""
        stack = NAV_STACKS.get(route, ["/"])

        # بدون چله‌ی انتخاب‌شده، ویوهای وابسته به چله ساخته نمی‌شوند
        if any(r in CHELEH_ROUTES for r in stack) and not self.current_cheleh:
            return ["/"]

        # صفحه‌ی روز بدون روزِ انتخاب‌شده بی‌معناست — تا /status می‌رویم
        if "/day" in stack and not self.selected_day:
            trimmed = [r for r in stack if r != "/day"]
            return trimmed or ["/"]

        return stack

    def route_change(self, e=None):
        page = self.page
        route = page.route or "/"
        page.views.clear()

        for r in self._stack_for_route(route):
            page.views.append(self._make_view(r))

        page.update()

    def _make_view(self, route: str) -> ft.View:
        """ساخت یک ویو بر اساس مسیر آن."""
        ch = self.current_cheleh
        subtitle = ch.display_name if ch else ""

        if route == "/add":
            return ft.View(
                route="/add",
                appbar=make_appbar(
                    title="افزودن چله جدید",
                    subtitle="یک مسیر تازه ۴۰ روزه",
                    show_back=True,
                    on_back=lambda e: self.go_back("/"),
                ),
                controls=[build_add_view(self)],
            )
        
        if route == "/science":
            return ft.View(
                route="/science",
                appbar=make_appbar(
                    title="پشتوانه‌ی علمی چله",
                    subtitle="مغز چگونه عادت می‌سازد",
                    show_back=True,
                    on_back=lambda e: self.go_back("/"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_science_view(self)],
            )

        if route == "/edit":
            return ft.View(
                route="/edit",
                appbar=make_appbar(
                    title="ویرایش چله",
                    subtitle=(self.editing_cheleh.display_name
                              if self.editing_cheleh else ""),
                    show_back=True,
                    on_back=lambda e: self.go_back("/"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_edit_view(self)],
            )

        if route == "/catchup":
            return ft.View(
                route="/catchup",  # ← باگ: قبلاً 'catchup' بدون اسلش بود
                appbar=make_appbar(
                    title="روزهای جامانده",
                    subtitle="",
                    show_back=True,
                    on_back=lambda e: self.go_back("/status"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_catchup_view(self)],
            )

        if route == "/day":
            return ft.View(
                route="/day",
                appbar=make_appbar(
                    title="جزئیات روز",
                    subtitle=(f"روز {self.selected_day}"
                              if self.selected_day else ""),
                    show_back=True,
                    on_back=lambda e: self.go_back("/status"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_day_detail_view(self)],
            )

        if route == "/status":
            return ft.View(
                route="/status",
                appbar=make_appbar(
                    title="وضعیت چله",
                    subtitle=subtitle,
                    show_back=True,
                    on_back=lambda e: self.go_back("/"),
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
            )

        if route == "/stats":
            return ft.View(
                route="/stats",
                appbar=make_appbar(
                    title="آمار و گزارش",
                    subtitle=subtitle,
                    show_back=True,
                    on_back=lambda e: self.go_back("/status"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_stats_view(self)],
            )

        if route == "/about":
            return ft.View(
                route="/about",
                appbar=make_appbar(
                    title="درباره برنامه",
                    show_back=True,
                    on_back=lambda e: self.go_back("/"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_about_view(self)],
            )

        # ---------- ریشه (/) ----------
        theme_icon = (ft.Icons.DARK_MODE if self.theme_mode == "light"
                      else ft.Icons.LIGHT_MODE)
        return ft.View(
            route="/",
            appbar=make_appbar(
                title="چله‌یار",
                actions=[
                    import_cheleh_action(self),
                    ft.IconButton(
                        ft.Icons.PSYCHOLOGY,
                        tooltip="پشتوانه علمی",
                        on_click=lambda e: self.navigate("/science"),
                    ),
                    ft.IconButton(
                        theme_icon,
                        tooltip="حالت شب/روز",
                        on_click=lambda e: self.page.run_task(self.toggle_theme),
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
        )

    # ----------------------------------------------------------------
    # تم
    # ----------------------------------------------------------------

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

    # ----------------------------------------------------------------
    # منطق چله
    # ----------------------------------------------------------------

    def check_missed_days(self):
        """اولین چله فعالی که روز ثبت‌نشده دارد را پیدا و به صفحه تعیین تکلیف برو"""
        for ch in self.chelehs:
            if ch.status == "active" and get_unrecorded_days(ch):
                self.current_cheleh = ch
                self.navigate("/catchup")
                return

    def fail_chelleh(self, c: Cheleh):
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
        self.db.save_cheleh(c)