"""صفحهٔ تنظیمات: فونت، قالب رنگی، پس‌زمینه (شامل تصویر و پالت استخراج‌شده)"""

import os
import json

import flet as ft

from theme import elevated_card
from theme_manager import FONT_CHOICES, COLOR_SCHEMES, BACKGROUNDS, pick_text_on


def _img_palette(db) -> list:
    """پالت ذخیره‌شدهٔ تصویر (لیست hex) یا لیست خالی"""
    try:
        pal = json.loads(db.get_setting("img_palette", "[]"))
        return [h for h in pal if isinstance(h, str) and h.startswith("#")]
    except Exception:
        return []


def build_settings_view(app) -> ft.Control:
    page = app.page
    db = app.db

    # ------------------------------------------------------------------
    # ۱) فونت
    # ------------------------------------------------------------------
    def on_font_select(e):
        key = e.control.value
        db.set_setting("font_family", key)
        app.apply_appearance()
        title = next((f["title"] for f in FONT_CHOICES if f["key"] == key), "پیش‌فرض")
        app.snack(f"فونت «{title}» اعمال شد ✅")

    font_dd = ft.Dropdown(
        label="فونت برنامه",
        value=db.get_setting("font_family", ""),
        filled=True,
        leading_icon=ft.Icons.TEXT_FIELDS,
        options=[
            ft.DropdownOption(key=f["key"], text=f["title"])
            for f in FONT_CHOICES
        ],
        on_select=on_font_select,
    )

    # ------------------------------------------------------------------
    # ۲) قالب رنگی (سواچ‌ها + گزینهٔ «از تصویر»)
    # ------------------------------------------------------------------
    swatches_row = ft.Row(spacing=10, run_spacing=10, wrap=True)

    def refresh_swatches():
        cur = db.get_setting("color_scheme", "green")
        pal = _img_palette(db)
        swatches_row.controls = []
        for s in COLOR_SCHEMES:
            is_sel = s["key"] == cur
            common = dict(
                width=42, height=42,
                border_radius=21,
                border=ft.Border.all(
                    3 if is_sel else 1,
                    ft.Colors.ON_SURFACE if is_sel
                    else ft.Colors.with_opacity(0.25, ft.Colors.GREY_500),
                ),
                tooltip=s["title"],
                on_click=lambda e, k=s["key"], t=s["title"]: pick_color(k, t),
            )
            if s["key"] == "custom":
                # سواچ چندرنگ: گرادیان از ۳ رنگ اول پالت استخراج‌شدهٔ تصویر
                colors = pal[:3] or ["#B0BEC5"]
                swatches_row.controls.append(ft.Container(
                    **common,
                    gradient=ft.LinearGradient(colors=colors),
                    content=ft.Icon(ft.Icons.CHECK, size=18,
                                    color=pick_text_on(colors[0])) if is_sel else None,
                ))
            else:
                swatches_row.controls.append(ft.Container(
                    **common,
                    bgcolor=s["swatch"],
                    content=ft.Icon(ft.Icons.CHECK, size=18,
                                    color=ft.Colors.WHITE) if is_sel else None,
                ))

    def pick_color(key: str, title: str):
        if key == "custom" and not _img_palette(db):
            app.snack("ابتدا از بخش «پس‌زمینه» یک تصویر انتخاب کنید ⚠️")
            return
        db.set_setting("color_scheme", key)
        app.apply_appearance()
        refresh_swatches()
        page.update()
        app.snack(f"قالب رنگی «{title}» اعمال شد ✅")

    refresh_swatches()

    # ------------------------------------------------------------------
    # ۳) پس‌زمینه (رنگ‌ها + تصویر)
    # ------------------------------------------------------------------
    bg_row = ft.Row(spacing=14, run_spacing=14, wrap=True)
    img_actions = ft.Row(spacing=8)   # دکمه‌های تغییر/حذف تصویر

    def make_bg_item(b: dict) -> ft.Control:
        is_sel = b["key"] == db.get_setting("background", "default")

        # --- گزینهٔ تصویر ---
        if b.get("is_image"):
            cur_img = db.get_setting("bg_image", "") or ""
            has_img = bool(cur_img) and os.path.exists(cur_img)
            is_sel = is_sel and has_img

            preview = ft.Container(
                content=(
                    ft.Image(src=cur_img, width=56, height=34,
                             fit=ft.BoxFit.COVER, border_radius=10)
                    if has_img else
                    ft.Icon(ft.Icons.ADD_PHOTO_ALTERNATE_OUTLINED,
                            size=20, color=ft.Colors.PRIMARY)
                ),
                width=56, height=34,
                alignment=ft.Alignment.CENTER,
                bgcolor=None if has_img else ft.Colors.SURFACE_CONTAINER_LOW,
                border_radius=10,
                border=ft.Border.all(
                    2 if is_sel else 1,
                    ft.Colors.ON_SURFACE if is_sel
                    else ft.Colors.with_opacity(0.25, ft.Colors.GREY_500),
                ),
            )
            return ft.Container(
                content=ft.Column([
                    preview,
                    ft.Text(
                        b["title"], size=10,
                        weight=ft.FontWeight.BOLD if is_sel else None,
                        color=ft.Colors.PRIMARY if is_sel else ft.Colors.GREY_600,
                    ),
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                tooltip="انتخاب تصویر پس‌زمینه از دستگاه",
                on_click=app.pick_background_image,   # ← پنجرهٔ انتخاب فایل
            )

        # --- گزینه‌های رنگی (مثل قبل) ---
        preview = ft.Container(
            content=(
                ft.Icon(ft.Icons.CHECK, size=16, color=ft.Colors.ON_SURFACE)
                if is_sel else
                (ft.Icon(ft.Icons.RESTORE, size=14, color=ft.Colors.GREY_500)
                 if b["light"] is None else None)
            ),
            width=56, height=34,
            bgcolor=b["light"] or ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=10,
            border=ft.Border.all(
                2 if is_sel else 1,
                ft.Colors.ON_SURFACE if is_sel
                else ft.Colors.with_opacity(0.25, ft.Colors.GREY_500),
            ),
        )
        return ft.Container(
            content=ft.Column([
                preview,
                ft.Text(
                    b["title"], size=10,
                    weight=ft.FontWeight.BOLD if is_sel else None,
                    color=ft.Colors.PRIMARY if is_sel else ft.Colors.GREY_600,
                ),
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            on_click=lambda e, k=b["key"], t=b["title"]: pick_bg(k, t),
        )

    def refresh_bg():
        bg_row.controls = [make_bg_item(b) for b in BACKGROUNDS]

    def refresh_img_actions():
        cur_img = db.get_setting("bg_image", "") or ""
        if cur_img and os.path.exists(cur_img):
            img_actions.controls = [
                ft.TextButton("تغییر تصویر", icon=ft.Icons.EDIT,
                              on_click=app.pick_background_image),
                ft.TextButton("حذف تصویر", icon=ft.Icons.DELETE_OUTLINE,
                              on_click=app.clear_background_image),
            ]
        else:
            img_actions.controls = []

    def pick_bg(key: str, title: str):
        db.set_setting("background", key)
        app.apply_appearance()
        refresh_bg()
        refresh_img_actions()
        page.update()
        app.snack(f"پس‌زمینه «{title}» اعمال شد ✅")

    refresh_bg()
    refresh_img_actions()

    # هوک: FilePicker در theme_mixin پس از انتخاب/حذف تصویر این را صدا می‌زند
    def _on_bg_changed():
        refresh_bg()
        refresh_img_actions()
        refresh_swatches()   # گرادیان سواچ «از تصویر» تازه شود
        page.update()

    app._on_bg_changed = _on_bg_changed

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    font_card = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.TEXT_FIELDS, size=18, color=ft.Colors.PRIMARY),
                ft.Text("فونت", size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            font_dd,
            ft.Text(
                "برای فونت‌های دلخواه (وزیرمتن، ساحل و…) باید فایل‌های فونت "
                "در assets برنامه باشند؛ در غیر این صورت فقط فونت‌های نصب‌شده "
                "روی دستگاه اثر دارند.",
                size=10, color=ft.Colors.GREY_500),
        ], spacing=10),
        padding=16,
    )

    color_card = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.PALETTE_OUTLINED, size=18, color=ft.Colors.PRIMARY),
                ft.Text("قالب رنگی", size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            swatches_row,
            ft.Text("سواچ چندرنگ، قالب برنامه را از رنگ‌های غالب تصویر پس‌زمینه می‌سازد.",
                    size=10, color=ft.Colors.GREY_500),
        ], spacing=10),
        padding=16,
    )

    background_card = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.WALLPAPER, size=18, color=ft.Colors.PRIMARY),
                ft.Text("پس‌زمینه", size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            bg_row,
            img_actions,
            ft.Text("با انتخاب «تصویر»، رنگ پس‌زمینه با تصویر جایگزین می‌شود؛ "
                    "قالب رنگی همچنان قابل ترکیب با رنگ‌های ساده است.",
                    size=10, color=ft.Colors.GREY_500),
        ], spacing=10),
        padding=16,
    )

    return ft.Column([
        ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton("بازگشت", icon=ft.Icons.ARROW_BACK,
                                  on_click=lambda e: app.navigate("/")),
                    ft.Container(expand=True),
                    ft.Text("تنظیمات", size=18, weight=ft.FontWeight.BOLD),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                font_card,
                color_card,
                background_card,
                ft.Container(height=24),
            ], spacing=14),
            padding=ft.Padding.only(left=16, right=16, top=8, bottom=8),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)