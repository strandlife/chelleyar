import flet as ft

from nav_config import NAV_STACKS, CHELEH_ROUTES
from theme import make_appbar, import_chelleh_action
from utils import to_persian_digits
from views.list_view import build_list_view
from views.day_detail_view import build_day_detail_view
from views.add_view import build_add_view
from views.status_view import build_status_view
from views.edit_view import build_edit_view
from views.stats_view import build_stats_view
from views.backup_view import build_backup_view
from views.catchup_view import build_catchup_view
from views.about_view import build_about_view
from views.science_view import build_science_view


# آستانه‌ی موبایل/دسکتاپ بر حسب پیکسل منطقی
# (کلاس‌های اندازه‌ی پنجره در Material: compact < 600)
DESKTOP_MIN_WIDTH = 600


class RouterMixin:
    """مسیریابی — استک ویوها از route مشتق می‌شود (single source of truth)"""

    # ----------------------------------------------------------------
    # موبایل / دسکتاپ
    # ----------------------------------------------------------------

    def _is_desktop(self) -> bool:
        """آیا پنجره آن‌قدر پهن است که اکشن‌ها مستقیم در appbar بیایند؟"""
        return (self.page.width or 0) >= DESKTOP_MIN_WIDTH

    def connect_resize(self):
        """اتصال رویداد تغییر اندازه — یک‌بار در main.py صدا زده شود.

        سازگار با نسخه‌های قدیمی و جدید فلت.
        """
        if hasattr(self.page, "on_resized"):
            self.page.on_resized = self.handle_resize
        else:  # نسخه‌های قدیمی‌تر فلت
            self.page.on_resize = self.handle_resize

    def handle_resize(self, e=None):
        """تغییر اندازه‌ی پنجره — فقط با عبور از آستانه بازسازی کن،
        نه با هر پیکسل (وگرنه فرم‌ها و اسکرول مدام ریست می‌شوند)."""
        wide = self._is_desktop()
        if wide != getattr(self, "_last_wide", None):
            self._last_wide = wide
            self.route_change(None)

    # ----------------------------------------------------------------
    # اکشن‌های ریسپانسیو appbar
    # ----------------------------------------------------------------

    @staticmethod
    def _to_menu_item(btn: ft.IconButton) -> ft.PopupMenuItem:
        """تبدیل IconButton به آیتم منوی سرریز (آیکن + متن tooltip).

        در Flet 1.0 سازنده‌ی PopupMenuItem دیگر text/icon ندارد و فقط
        content می‌گیرد؛ پس آیکن و متن را خودمان در یک Row می‌چینیم.
        (در حالت RTL خودکار راست‌به‌چپ چیده می‌شود: آیکن راست، متن چپ)
        """
        controls: list[ft.Control] = []
        if btn.icon:
            controls.append(ft.Icon(btn.icon))
        controls.append(ft.Text(btn.tooltip or ""))
        return ft.PopupMenuItem(
            content=ft.Row(spacing=12, controls=controls),
            on_click=btn.on_click,
        )

    def _responsive_actions(
        self,
        pinned: list[ft.Control],
        collapsible: list[ft.IconButton],
    ) -> list[ft.Control]:
        """دسکتاپ: همه به‌صورت آیکن.
        موبایل: pinned ثابت می‌ماند و بقیه در منوی «بیشتر» جمع می‌شوند."""
        if self._is_desktop() or not collapsible:
            return pinned + collapsible
        menu_btn = ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT,
            tooltip="بیشتر",
            items=[self._to_menu_item(b) for b in collapsible],
        )
        return pinned + [menu_btn]

    # ----------------------------------------------------------------
    # مسیریابی — استک ویوها از route مشتق می‌شود (single source of truth)
    # ----------------------------------------------------------------

    def _stack_for_route(self, route: str) -> list[str]:
        """استک ویوهای معتبر برای مسیر فعلی + محافظ deep-link/reload."""
        stack = NAV_STACKS.get(route, ["/"])

        # بدون چله‌ی انتخاب‌شده، ویوهای وابسته به چله ساخته نمی‌شوند
        if any(r in CHELEH_ROUTES for r in stack) and not self.current_chelleh:
            return ["/"]

        # صفحه‌ی روز بدون روزِ انتخاب‌شده بی‌معناست — تا /status می‌رویم
        if "/day" in stack and not self.selected_day:
            trimmed = [r for r in stack if r != "/day"]
            return trimmed or ["/"]

        return stack

    def route_change(self, e=None):
        page = self.page
        route = page.route or "/"
        self._last_wide = self._is_desktop()   # ← برای handle_resize
        page.views.clear()

        for r in self._stack_for_route(route):
            page.views.append(self._make_view(r))

        page.update()

    def _make_view(self, route: str) -> ft.View:
        """ساخت یک ویو بر اساس مسیر آن."""
        ch = self.current_chelleh
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

        if route == "/backup":
            return ft.View(
                route="/backup",
                appbar=make_appbar(
                    title="پشتیبان‌گیری",
                    subtitle="صدور و ورود داده‌ها",
                    show_back=True,
                    on_back=lambda e: self.go_back("/"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_backup_view(self)],
            )

        if route == "/edit":
            return ft.View(
                route="/edit",
                appbar=make_appbar(
                    title="ویرایش چله",
                    subtitle=(self.editing_chelleh.display_name
                              if self.editing_chelleh else ""),
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
                    subtitle=(f"روز {to_persian_digits(str(self.selected_day))}"
                              if self.selected_day else ""),
                    show_back=True,
                    on_back=lambda e: self.go_back("/status"),
                ),
                scroll=ft.ScrollMode.AUTO,
                controls=[build_day_detail_view(self)],
            )

        if route == "/status":
            # یک اکشن دارد؛ در موبایل هم جا می‌شود — بدون تغییر
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

        # این‌ها در موبایل هم ثابت می‌مانند (پرکاربردترین‌ها)
        pinned = [
            import_chelleh_action(self),
            ft.IconButton(
                theme_icon,
                tooltip="حالت شب/روز",
                on_click=lambda e: self.page.run_task(self.toggle_theme),
            ),
        ]
        # این‌ها در موبایل داخل منوی سرریز می‌روند
        collapsible = [
            ft.IconButton(
                ft.Icons.PSYCHOLOGY,
                tooltip="پشتوانه علمی",
                on_click=lambda e: self.navigate("/science"),
            ),
            ft.IconButton(
                ft.Icons.BACKUP_OUTLINED,
                tooltip="پشتیبان‌گیری",
                on_click=lambda e: self.navigate("/backup"),
            ),
            ft.IconButton(
                ft.Icons.INFO_OUTLINE,
                tooltip="درباره",
                on_click=lambda e: self.navigate("/about"),
            ),
        ]

        return ft.View(
            route="/",
            appbar=make_appbar(
                title="چله‌یار",
                actions=self._responsive_actions(pinned, collapsible),
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