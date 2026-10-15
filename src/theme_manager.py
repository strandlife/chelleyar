import flet as ft


class ThemeMixin:
    """مدیریت حالت شب/روز"""

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