from datetime import date
import jdatetime
from farscal import open_date_dialog, format_jdate
import datetime
import uuid

import flet as ft

from models import Chelleh
from theme import elevated_card
from utils import COLOR_OPTIONS, to_jalali
from ready_chellehs import build_ready_section

MAX_LEVELS = 10
MIN_LEVELS = 2


def _to_jd(gd: date) -> jdatetime.date:
    """میلادی → شمسی (jdatetime.date)"""
    return jdatetime.date.fromgregorian(date=gd)


def _new_level_id() -> str:
    return str(uuid.uuid4())


def _new_level(title: str, score: int, color: str) -> dict:
    return {"id": _new_level_id(), "title": title, "score": score, "color": color}


def build_add_view(app) -> ft.Control:
    page = app.page

    # ---------- فیلدهای اصلی ----------
    name_field = ft.TextField(
        label="نام اصلی چله",
        hint_text="مثلاً: چله نماز صبح",
        border_radius=12,
        filled=True,
        prefix_icon=ft.Icons.LABEL_OUTLINE,
    )
    display_field = ft.TextField(
        label="نام نمایشی",
        hint_text="در لیست چله‌ها نمایش داده می‌شود",
        border_radius=12,
        filled=True,
        prefix_icon=ft.Icons.VISIBILITY_OUTLINED,
    )
    task_field = ft.TextField(
        label="وظیفه‌ای که باید مراقبت شود",
        hint_text="مثلاً: خواندن نماز صبح در اول وقت",
        multiline=True, min_lines=2,
        border_radius=12,
        filled=True,
        prefix_icon=ft.Icons.TASK_ALT_OUTLINED,
    )

    # ---------- سطوح (منبع اصلی داده) ----------
    levels: list[dict] = [
        _new_level("", 1, "#2E7D32"),
        _new_level("", 2, "#4CAF50"),
        _new_level("", 3, "#8BC34A"),
    ]
    levels_column = ft.Column(spacing=8)
    levels_counter = ft.Text(size=11, color=ft.Colors.GREY_500)

    def _find_index(level_id: str) -> int | None:
        for i, lv in enumerate(levels):
            if lv.get("id") == level_id:
                return i
        return None

    # ---------- دیالوگ افزودن / ویرایش سطح ----------
    def open_level_dialog(e=None, level_id: str | None = None):
        idx = _find_index(level_id) if level_id else None
        is_edit = idx is not None
        initial = dict(levels[idx]) if is_edit else {
            "title": "", "score": "", "color": "#4CAF50"}

        title_field = ft.TextField(
            label="عنوان سطح",
            hint_text="مثلاً: نماز صبح اول وقت",
            value=initial["title"],
            border_radius=10,
            filled=True,
            autofocus=True,
            prefix_icon=ft.Icons.LABEL_OUTLINE,
        )
        score_field = ft.TextField(
            label="امتیاز",
            hint_text="عدد مثبت؛ مثلاً 5",
            value=str(initial["score"]),
            border_radius=10,
            filled=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.STAR_OUTLINE,
        )
        color_dd = ft.Dropdown(
            label="رنگ",
            value=initial["color"],
            border_radius=10,
            filled=True,
            options=[ft.DropdownOption(key=k, text=t)
                     for k, t in COLOR_OPTIONS],
        )
        preview = ft.Container(
            width=36, height=36,
            bgcolor=initial["color"],
            border_radius=10,
            border=ft.Border.all(2, ft.Colors.with_opacity(0.15, ft.Colors.BLACK)),
        )

        def on_color_change(e):
            preview.bgcolor = color_dd.value
            page.update()

        color_dd.on_change = on_color_change

        def clear_errors(e=None):
            title_field.error_text = None
            score_field.error_text = None
            page.update()

        title_field.on_change = clear_errors
        score_field.on_change = clear_errors

        def save(e):
            t = title_field.value.strip()
            if not t:
                title_field.error_text = "عنوان سطح را وارد کنید"
                page.update()
                return

            raw = (score_field.value or "").strip()
            if not raw:
                score_field.error_text = "امتیاز را وارد کنید"
                page.update()
                return
            try:
                s = int(raw)
            except ValueError:
                score_field.error_text = "امتیاز باید عدد باشد"
                page.update()
                return
            if s < 0:
                score_field.error_text = "امتیاز نمی‌تواند منفی باشد"
                page.update()
                return

            # جلوگیری از امتیاز تکراری (سطحِ در حال ویرایش مستثنا می‌شود)
            if any(lv["score"] == s and lv["id"] != initial.get("id")
                   for lv in levels):
                score_field.error_text = "این امتیاز قبلاً استفاده شده است"
                page.update()
                return

            data = {
                "id": initial.get("id") or _new_level_id(),
                "title": t,
                "score": s,
                "color": color_dd.value or "#4CAF50",
            }
            if is_edit:
                levels[idx] = data
            else:
                levels.append(data)
            refresh_levels()
            page.pop_dialog()

        # Enter در فیلد امتیاز = ذخیره
        score_field.on_submit = save

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.LAYERS_OUTLINED, size=20,
                        color=ft.Colors.PRIMARY),
                ft.Text("ویرایش سطح" if is_edit else "افزودن سطح",
                        size=16, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            content=ft.Column([
                title_field,
                score_field,
                ft.Row([
                    ft.Container(content=color_dd, expand=True),
                    preview,
                ], spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], tight=True, spacing=12),
            actions=[
                ft.TextButton(
                    "انصراف",
                    on_click=lambda e: page.pop_dialog(),
                ),
                ft.Button(
                    "ذخیره",
                    icon=ft.Icons.CHECK,
                    on_click=save,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.WHITE,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.show_dialog(dlg)

    # ---------- نمایش خلاصه سطوح ----------
    def make_level_tile(lv: dict) -> ft.Container:
        score_chip = ft.Container(
            content=ft.Text(f"امتیاز {lv['score']}", size=11,
                            weight=ft.FontWeight.BOLD, color=lv["color"]),
            bgcolor=ft.Colors.with_opacity(0.12, lv["color"]),
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            border_radius=20,
        )
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    width=14, height=14,
                    bgcolor=lv["color"], border_radius=7,
                    border=ft.Border.all(
                        1, ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
                ),
                ft.Text(
                    lv["title"] or "بدون عنوان",
                    size=13, weight=ft.FontWeight.W_600,
                    expand=True,
                    italic=not lv["title"],
                    color=ft.Colors.GREY_500 if not lv["title"] else None,
                ),
                score_chip,
                ft.IconButton(
                    ft.Icons.EDIT_OUTLINED, icon_size=18,
                    tooltip="ویرایش سطح",
                    icon_color=ft.Colors.GREY_700,
                    on_click=lambda e, lid=lv["id"]: open_level_dialog(level_id=lid),
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE, icon_size=18,
                    tooltip="حذف سطح",
                    icon_color=ft.Colors.RED_400,
                    on_click=lambda e, lid=lv["id"]: remove_level(lid),
                ),
            ], spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=12,
            border=ft.Border.all(
                1, ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY)),
        )

    def refresh_levels():
        levels_column.controls.clear()
        for lv in levels:
            levels_column.controls.append(make_level_tile(lv))
        levels_counter.value = f"{len(levels)} از {MAX_LEVELS} سطح"
        page.update()

    # ---------- چله‌های آماده ----------
    def apply_template(tpl: dict):
        name_field.value = tpl["name"]
        display_field.value = tpl.get("display_name") or tpl["name"]
        task_field.value = tpl.get("task", "")
        levels.clear()
        for lv in tpl["levels"]:
            levels.append(_new_level(lv["title"], lv["score"], lv["color"]))
        refresh_levels()
        app.snack(f"چله آماده «{tpl['name']}» بارگذاری شد ✅")

    ready_section = build_ready_section(app, apply_template)

    def remove_level(level_id: str):
        idx = _find_index(level_id)
        if idx is None:
            return
        if len(levels) <= MIN_LEVELS:
            app.snack("حداقل دو سطح لازم است")
            return
        levels.pop(idx)
        refresh_levels()

    def add_level_click(e=None):
        if len(levels) >= MAX_LEVELS:
            app.snack("حداکثر ۱۰ سطح مجاز است")
            return
        open_level_dialog()

    refresh_levels()

    # ---------- تاریخ شروع ----------
    selected_start_date = {"value": date.today()}      # میلادی — مثل قبل
    start_date_text = ft.Text(
        format_jdate(_to_jd(selected_start_date["value"]), "WWWW d MMMM yyyy"),
        size=13, weight=ft.FontWeight.BOLD,
    )

    def on_start_date_changed(jd: jdatetime.date):
        selected_start_date["value"] = jd.togregorian()   # ذخیره میلادی — مدل دست‌نخورده
        start_date_text.value = format_jdate(_to_jd(selected_start_date["value"]), "WWWW d MMMM yyyy")
        page.update()

    def open_picker(e):
        open_date_dialog(
            page,
            value=_to_jd(selected_start_date["value"]),
            #min_date=_to_jd(date.today()),   # شروع از امروز؛ اگر اجازه‌ی تاریخ گذشته می‌خواهید حذف کنید
            on_selected=on_start_date_changed,
            title="انتخاب تاریخ شروع چله",
        )

    # ---------- ثبت فرم ----------
    async def submit(e):
        name = name_field.value.strip()
        if not name:
            app.snack("نام چله را وارد کنید")
            return

        if any(not lv["title"].strip() for lv in levels):
            app.snack("عنوان همه سطوح را وارد کنید (روی آیکون ویرایش بزنید)")
            return

        if len(levels) < MIN_LEVELS:
            app.snack("حداقل دو سطح وظیفه تعریف کنید")
            return

        # افزودن خودکار سطح شکست
        if not any(lv["score"] == 0 for lv in levels):
            levels.append(_new_level("شکست", 0, "#C62828"))

        start_date_iso = selected_start_date["value"].isoformat()

        c = Chelleh(
            id=str(uuid.uuid4()),
            name=name,
            display_name=display_field.value.strip() or name,
            task=task_field.value.strip(),
            levels=levels,
            cycle_number=1,
            cycle_start_date=start_date_iso,
            total_days=40,
            current_day=1,
            daily_logs={},
            history=[],
            status="active",
        )
        app.chellehs.append(c)
        app.db.save_chelleh(c)
        app.snack("چله با موفقیت ساخته شد 🎉")
        await page.push_route("/")

    # ---------- UI ----------
    basic_info = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("اطلاعات پایه", size=14,
                        weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=4),
            name_field,
            display_field,
            task_field,
        ], spacing=10),
        padding=16,
    )

    levels_section = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LAYERS_OUTLINED, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("سطوح وظیفه", size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                levels_counter,
                ft.TextButton(
                    "افزودن سطح",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    on_click=add_level_click,
                ),
            ], spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=14,
                            color=ft.Colors.AMBER_700),
                    ft.Text(
                        "با دکمه «افزودن سطح» یک سطح جدید تعریف کنید. "
                        "با کسب حداقل ۱ امتیاز، چله در آن روز برقرار می‌ماند.",
                        size=11, color=ft.Colors.GREY_600),
                ], spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.START),
                padding=ft.Padding.symmetric(vertical=8, horizontal=10),
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.AMBER),
                border_radius=10,
            ),
            levels_column,
        ], spacing=12),
        padding=16,
    )

    date_section = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("تاریخ شروع", size=14,
                        weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=4),
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.EVENT_AVAILABLE,
                                        color=ft.Colors.GREEN_700, size=22),
                        padding=8,
                        bgcolor=ft.Colors.with_opacity(
                            0.12, ft.Colors.GREEN),
                        border_radius=10,
                    ),
                    ft.Column([
                        ft.Text("تاریخ شروع چله", size=10,
                                color=ft.Colors.GREY_600),
                        start_date_text,
                    ], spacing=0, expand=True),
                    ft.TextButton(
                        "تغییر",
                        icon=ft.Icons.EDIT_CALENDAR,
                        on_click=open_picker,
                    ),
                ], spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding.symmetric(vertical=8, horizontal=10),
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border_radius=12,
            ),
        ], spacing=8),
        padding=16,
    )

    actions = ft.Row([
        ft.TextButton(
            "انصراف",
            icon=ft.Icons.CLOSE,
            on_click=lambda e: app.navigate("/"),
            style=ft.ButtonStyle(color=ft.Colors.GREY_600),
        ),
        ft.Container(expand=True),
        ft.Button(
            "ثبت چله",
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            on_click=submit,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.WHITE,
                padding=ft.Padding.symmetric(vertical=14, horizontal=28),
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=2,
            ),
        ),
    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Column([
        ft.Container(
            content=ft.Column([
                ready_section,
                basic_info,
                levels_section,
                date_section,
                actions,
                ft.Container(height=24),
            ], spacing=14),
            padding=ft.Padding.only(left=16, right=16, top=16, bottom=8),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)