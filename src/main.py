import flet as ft
from app import ChelehApp
from database import Database
from theme import app_theme, app_dark_theme



FONT_URL = "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/webfonts/Vazirmatn-Regular.woff2"
FONT_BOLD_URL = "https://github.com/rastikerdar/vazirmatn/raw/master/fonts/webfonts/Vazirmatn-Bold.woff2"



async def main(page: ft.Page):
    page.title = "چله‌یار"
    page.rtl = True
    page.adaptive = True

    page.fonts = {
        "Vazirmatn": FONT_URL,
        "Vazirmatn Bold": FONT_BOLD_URL,
    }
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = app_theme()
    page.dark_theme = app_dark_theme()

    db = Database()

    # ساخت و راه‌اندازی اپلیکیشن
    app = ChelehApp(page, db)
    await app.init()

    page.on_route_change = app.route_change
    app.route_change(None)


if __name__ == "__main__":
    ft.run(main)