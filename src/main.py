import flet as ft
from app import ChellehApp
from database import Database
from theme import app_theme, app_dark_theme




async def main(page: ft.Page):
    storage_paths = ft.StoragePaths()
    log_path = await storage_paths.get_console_log_filename()
    print(f"Console log path: {log_path}")
    page.title = "چله‌یار"
    page.rtl = True
    page.adaptive = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = app_theme()
    page.dark_theme = app_dark_theme()

    db = Database()

    # ساخت و راه‌اندازی اپلیکیشن
    app = ChellehApp(page, db)
    app.connect_resize()
    await app.init()
    app.setup_auto_lock()

    page.on_route_change = app.route_change
    page.on_view_pop = app.view_pop
    app.route_change(None)


if __name__ == "__main__":
    ft.run(main)