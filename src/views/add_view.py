from datetime import date
import datetime
import uuid

import flet as ft

from models import Cheleh
from theme import elevated_card
from utils import COLOR_OPTIONS, to_jalali

MAX_LEVELS = 10
MIN_LEVELS = 2


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
        {"title": "", "score": 1, "color": "#2E7D32"},
        {"title": "", "score": 2, "color": "#4CAF50"},
        {"title": "", "score": 3, "color": "#8BC34A"},
    ]
    levels_column = ft.Column(spacing=8)
    levels_counter = ft.Text(size=11, color=ft.Colors.GREY_500)

    # ---------- دیالوگ افزودن / ویرایش سطح ----------
    def open_level_dialog(e=None, index: int | None = None):
        is_edit = index is not None
        initial = dict(levels[index]) if is_edit else {
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

            # جلوگیری از امتیاز تکراری
            if any(lv["score"] == s
                   for i_lv, lv in enumerate(levels) if i_lv != index):
                score_field.error_text = "این امتیاز قبلاً استفاده شده است"
                page.update()
                return

            data = {"title": t, "score": s,
                    "color": color_dd.value or "#4CAF50"}
            if is_edit:
                levels[index] = data
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
    def make_level_tile(index: int, lv: dict) -> ft.Container:
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
                    on_click=lambda e, i=index: open_level_dialog(index=i),
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE, icon_size=18,
                    tooltip="حذف سطح",
                    icon_color=ft.Colors.RED_400,
                    on_click=lambda e, i=index: remove_level(i),
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
        for i, lv in enumerate(levels):
            levels_column.controls.append(make_level_tile(i, lv))
        levels_counter.value = f"{len(levels)} از {MAX_LEVELS} سطح"
        page.update()

    def remove_level(index: int):
        if len(levels) <= MIN_LEVELS:
            app.snack("حداقل دو سطح لازم است")
            return
        levels.pop(index)
        refresh_levels()

    def add_level_click(e=None):
        if len(levels) >= MAX_LEVELS:
            app.snack("حداکثر ۱۰ سطح مجاز است")
            return
        open_level_dialog()

    refresh_levels()

    # ---------- تاریخ شروع ----------
    selected_start_date = {"value": date.today()}
    start_date_text = ft.Text(
        to_jalali(selected_start_date["value"]),
        size=13, weight=ft.FontWeight.BOLD,
    )

    def on_date_picked(e):
        if picker.value:
            selected_start_date["value"] = picker.value.date()
            start_date_text.value = to_jalali(selected_start_date["value"])
            page.update()

    picker = ft.DatePicker(
        first_date=datetime.datetime(2020, 1, 1),
        last_date=datetime.datetime(2030, 12, 31),
        on_change=on_date_picked,
    )

    def open_picker(e):
        page.show_dialog(picker)

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
            levels.append({
                "title": "شکست",
                "score": 0,
                "color": "#C62828",
            })

        start_date_iso = selected_start_date["value"].isoformat()

        c = Cheleh(
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
        app.chelehs.append(c)
        app.db.save_cheleh(c)
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
                basic_info,
                levels_section,
                date_section,
                actions,
                ft.Container(height=24),
            ], spacing=14),
            padding=ft.Padding.only(left=16, right=16, top=16, bottom=8),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)