import flet as ft
import base64
import json
import uuid
from datetime import date
from models import Chelleh
from urllib.parse import unquote



# ---------- پالت رنگ ----------
PRIMARY = "#0D47A1"          # آبی نیلی
PRIMARY_LIGHT = "#1976D2"
ACCENT = "#FFB300"           # طلایی
SUCCESS = "#2E7D32"
DANGER = "#C62828"
SURFACE = "#F5F7FA"
SURFACE_DARK = "#121212"
CARD_BG = "#FFFFFF"
CARD_BG_DARK = "#1E1E1E"


def make_appbar(
    title: str,
    subtitle: str = "",
    show_back: bool = False,
    on_back=None,
    actions: list | None = None,
) -> ft.AppBar:
    """ساخت AppBar یکپارچه برای همه صفحات"""
    leading = None
    if show_back:
        leading = ft.IconButton(
            ft.Icons.ARROW_FORWARD,   # در RTL به معنای بازگشت
            icon_color=ft.Colors.PRIMARY,
            tooltip="بازگشت",
            on_click=on_back,
        )

    title_control = ft.Column([
        ft.Text(title, size=16, weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY),
        *( [ft.Text(subtitle, size=11, color=ft.Colors.GREY_600,
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)]
           if subtitle else [] ),
    ], spacing=0, alignment=ft.MainAxisAlignment.CENTER)

    return ft.AppBar(
        leading=leading,
        leading_width=48 if show_back else 0,
        title=title_control,
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        elevation=0,
        actions=actions or [],
    )


# ---------- تم اصلی ----------
def app_theme() -> ft.Theme:
    return ft.Theme(
        font_family="Vazirmatn",
        color_scheme_seed=PRIMARY,
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            secondary=ACCENT,
            surface=SURFACE,
            error=DANGER,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def app_dark_theme() -> ft.Theme:
    return ft.Theme(
        font_family="Vazirmatn",
        color_scheme_seed=PRIMARY_LIGHT,
        color_scheme=ft.ColorScheme(
            primary=PRIMARY_LIGHT,
            secondary=ACCENT,
            surface=SURFACE_DARK,
            error=DANGER,
        ),
    )


# ---------- سبک‌های مشترک ----------
def elevated_card(content: ft.Control, padding: int = 14,
                  radius: int = 16) -> ft.Container:
    """کارت با گوشه گرد و سایه ملایم"""
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=radius,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=12,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
    )

def gradient_header(title: str, subtitle: str = "",
                    icon=None) -> ft.Container:
    """هدر گرادیانی برای صفحات"""
    row_children = []
    if icon:
        row_children.append(ft.Icon(icon, color=ft.Colors.WHITE, size=28))
    row_children.append(
        ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            *( [ft.Text(subtitle, size=12,
                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE))]
               if subtitle else [] ),
        ], spacing=2, expand=True)
    )

    return ft.Container(
        content=ft.Row(row_children, spacing=12,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=18, horizontal=20),
        border_radius=ft.BorderRadius.only(
            bottom_left=20, bottom_right=20),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_RIGHT,
            end=ft.Alignment.BOTTOM_LEFT,
            colors=[PRIMARY, PRIMARY_LIGHT],
        ),
    )


def empty_state(icon, title: str, subtitle: str = "",
                action=None) -> ft.Container:
    """حالت خالی زیبا"""
    controls = [
        ft.Container(
            content=ft.Icon(icon, size=64,
                            color=ft.Colors.with_opacity(0.35, PRIMARY)),
            padding=20,
        ),
        ft.Text(title, size=17, weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREY_700),
    ]
    if subtitle:
        controls.append(
            ft.Text(subtitle, size=13, color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER)
        )
    if action:
        controls.append(ft.Container(content=action, margin=ft.Margin.only(top=12)))

    return ft.Container(
        content=ft.Column(controls, spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment.CENTER,
        padding=40,
    )

# ==================================================================
# دریافت چله از کد اشتراک‌گذاری (Import)
# ==================================================================

SHARE_PREFIX = "CHELEHYAR1:"


def _get_service(page: ft.Page, service_type):
    """سرویس موردنظر را از page.services برمی‌گرداند؛ اگر نبود می‌سازد."""
    for s in getattr(page, "services", []):
        if isinstance(s, service_type):
            return s
    svc = service_type()
    page.services.append(svc)
    return svc


def parse_share_code(code: str) -> dict:
    """کد اشتراک‌گذاری را پاک‌سازی، اعتبارسنجی و تجزیه می‌کند.

    ValueError با پیام فارسی در صورت خرابی کد.
    """
    if not code or not code.strip():
        raise ValueError("کد را وارد کنید")

    # پاک‌سازی: URL-encoding (کپی از ایمیل/پیام‌رسان) + فاصله‌ها و شکست خط
    cleaned = unquote(code.strip())
    cleaned = "".join(cleaned.split())

    prefix_len = len(SHARE_PREFIX)
    if cleaned[:prefix_len].upper() != SHARE_PREFIX:
        raise ValueError("کد معتبر نیست — باید با CHELEHYAR1: شروع شود")

    b64 = cleaned[prefix_len:]
    try:
        b64 += "=" * (-len(b64) % 4)   # جبران padding ناقص
        raw = base64.urlsafe_b64decode(b64.encode("ascii"))
        data = json.loads(raw.decode("utf-8"))
    except Exception:
        raise ValueError("کد خراب است؛ متن کامل کد را یک‌جا کپی کنید")

    if not isinstance(data, dict):
        raise ValueError("ساختار کد معتبر نیست")

    name = str(data.get("name") or "").strip()
    if not name:
        raise ValueError("کد فاقد نام چله است")

    # ---- سطوح ----
    raw_levels = data.get("levels")
    if not isinstance(raw_levels, list):
        raise ValueError("سطوح چله در کد معتبر نیست")

    levels = []
    for lv in raw_levels:
        if not isinstance(lv, dict):
            continue
        title = str(lv.get("title") or "").strip()
        if not title:
            continue
        try:
            score = max(0, int(lv.get("score", 0)))
        except (TypeError, ValueError):
            score = 0
        levels.append({
            "title": title,
            "score": score,
            "color": str(lv.get("color") or "#4CAF50"),
        })

    if len(levels) < 2:
        raise ValueError("سطوح چله معتبر نیست (حداقل دو سطح لازم است)")

    # سطح شکست خودکار
    if not any(lv["score"] == 0 for lv in levels):
        levels.append({"title": "شکست", "score": 0, "color": "#C62828"})

    try:
        total_days = min(max(int(data.get("total_days", 40)), 1), 400)
    except (TypeError, ValueError):
        total_days = 40

    return {
        "name": name,
        "display_name": str(data.get("display_name") or name).strip(),
        "task": str(data.get("task") or "").strip(),
        "levels": levels,
        "total_days": total_days,
    }

def show_import_dialog(app):
    page = app.page

    code_field = ft.TextField(
        label="کد چله",
        hint_text="کد دریافتی را اینجا بچسبانید",
        multiline=True,
        min_lines=3,
        max_lines=6,
        filled=True,
        border=ft.OutlineInputBorder(
            border_radius=ft.BorderRadius.all(12)),
        suffix=ft.IconButton(
            ft.Icons.CONTENT_PASTE,
            tooltip="چسباندن از کلیپ‌بورد",
            icon_size=18,
            on_click=None,   # پایین‌تر ست می‌شود
        ),
    )

    preview_col = ft.Column(visible=False, spacing=6)
    parsed = {"data": None}

    def make_preview(d: dict) -> list:
        level_rows = []
        for lv in d["levels"]:
            level_rows.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(width=10, height=10,
                                     bgcolor=lv["color"],
                                     border_radius=5),
                        ft.Text(lv["title"], size=12, expand=True,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(f"امتیاز {lv['score']}",
                                size=10, color=ft.Colors.GREY_600),
                    ], spacing=8),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=5),
                    bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                    border_radius=8,
                )
            )
        return [
            ft.Row([
                ft.Icon(ft.Icons.INBOX, size=16, color=ft.Colors.PRIMARY),
                ft.Text(d["display_name"], size=14,
                        weight=ft.FontWeight.BOLD, expand=True,
                        max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f"{d['total_days']} روز",
                        size=10, color=ft.Colors.GREY_600),
            ], spacing=6),
            ft.Text(d["task"] or "بدون توضیح وظیفه",
                    size=11, color=ft.Colors.GREY_600,
                    max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            *level_rows,
        ]

    def check_code(e=None):
        try:
            d = parse_share_code(code_field.value or "")
        except ValueError as ex:
            parsed["data"] = None
            code_field.error_text = str(ex)
            preview_col.visible = False
            page.update()
            return
        code_field.error_text = None
        parsed["data"] = d
        preview_col.controls = make_preview(d)
        preview_col.visible = True
        page.update()

    async def paste_from_clipboard(e=None):
        try:
            clipboard = _get_service(page, ft.Clipboard)
            text = await clipboard.get()
            if text:
                code_field.value = text.strip()
                page.update()
                check_code()
        except Exception:
            app.snack("دسترسی به کلیپ‌بورد ممکن نشد")

    code_field.suffix.on_click = paste_from_clipboard

    # ---------- منطق واقعی import (بدون UI) ----------
    async def perform_import():
        d = parsed["data"]
        if d is None:
            # یک بار دیگر بررسی می‌کنیم
            check_code()
            d = parsed["data"]
        if d is None:
            app.snack("کد معتبر نیست")
            return

        c = Chelleh(
            id=str(uuid.uuid4()),
            name=d["name"],
            display_name=d["display_name"] or d["name"],
            task=d["task"],
            levels=d["levels"],
            cycle_number=1,
            cycle_start_date=date.today().isoformat(),
            total_days=d["total_days"],
            current_day=1,
            daily_logs={},
            history=[],
            status="active",
        )
        app.chellehs.append(c)
        app.db.save_chelleh(c)
        app.snack(f"چله «{c.display_name}» اضافه شد 🎉")
        app.refresh()

    # ---------- کنترل بستن دیالوگ ----------
    def on_cancel(e):
        dialog._confirmed = False
        page.pop_dialog()

    def on_confirm(e):
        # اعتبارسنجی سریع قبل از بستن دیالوگ
        if parsed["data"] is None:
            check_code()
            if parsed["data"] is None:
                return   # خطا زیر فیلد نمایش داده شده، دیالوگ باز می‌ماند
        dialog._confirmed = True
        page.pop_dialog()

    def on_dismiss(e):
        if getattr(dialog, "_confirmed", False):
            page.run_task(perform_import)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.INBOX, size=20, color=ft.Colors.PRIMARY),
            ft.Text("دریافت چله", size=16, weight=ft.FontWeight.BOLD),
        ], spacing=8),
        content=ft.Container(
            width=320,
            content=ft.Column([
                ft.Text(
                    "کدی که برایتان فرستاده‌اند را بچسبانید و "
                    "«بررسی کد» را بزنید تا پیش‌نمایش چله را ببینید.",
                    size=11, color=ft.Colors.GREY_600),
                code_field,
                preview_col,
            ], tight=True, spacing=10),
        ),
        actions=[
            ft.TextButton("انصراف", on_click=on_cancel),
            ft.TextButton("بررسی کد", icon=ft.Icons.QR_CODE_SCANNER,
                          on_click=check_code),
            ft.Button(
                "افزودن چله",
                icon=ft.Icons.ADD_CIRCLE,
                on_click=on_confirm,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=on_dismiss,
    )
    dialog._confirmed = False
    page.show_dialog(dialog)

def import_chelleh_action(app) -> ft.IconButton:
    """دکمه «دریافت چله» برای قرارگیری در actions اپ‌بار"""
    return ft.IconButton(
        ft.Icons.INBOX_OUTLINED,
        tooltip="دریافت چله از کد",
        icon_color=ft.Colors.PRIMARY,
        on_click=lambda e: show_import_dialog(app),
    )