import flet as ft

from models import Chelleh


class NavigationMixin:
    """ناوبری: جلو/عقب، بازسازی و بازکردن صفحات وابسته به چله.

    روی attributeهای تعریف‌شده در ChellehApp تکیه دارد:
    page, current_chelleh, editing_chelleh
    """

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
        self.editing_chelleh = ch
        self.navigate("/edit")

    def open_stats(self, ch):
        """رفتن به صفحه آمار برای یک چله"""
        self.current_chelleh = ch
        self.navigate("/stats")

    def open_status(self, ch: Chelleh):
        """رفتن به صفحه وضعیت یک چله"""
        self.current_chelleh = ch
        self.navigate("/status")