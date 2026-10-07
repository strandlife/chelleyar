from datetime import date
import datetime
import uuid

import flet as ft

from models import Cheleh
from theme import elevated_card
from utils import COLOR_OPTIONS, to_jalali


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

    levels_column = ft.Column(spacing=10)

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

    # ---------- ردیف سطح ----------
    def make_level_row(title: str = "", score: str = "1",
                       color: str = "#4CAF50") -> ft.Container:
        title_field = ft.TextField(
            label="عنوان سطح",
            value=title,
            hint_text="مثلاً: نماز صبح اول وقت",
            border_radius=10,
            filled=True,
            dense=True,
            expand=True,
        )
        score_field = ft.TextField(
            label="امتیاز",
            value=score,
            width=95,
            border_radius=10,
            filled=True,
            dense=True,
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        color_dd = ft.Dropdown(
            label="رنگ",
            value=color,
            width=150,
            border_radius=10,
            filled=True,
            dense=True,
            options=[ft.DropdownOption(key=k, text=t)
                     for k, t in COLOR_OPTIONS],
        )

        preview = ft.Container(
            width=32, height=32,
            bgcolor=color,
            border_radius=8,
            border=ft.Border.all(2, ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
        )

        def on_color_change(e, dd=color_dd, pv=preview):
            pv.bgcolor = dd.value
            page.update()

        color_dd.on_change = on_color_change

        remove_btn = ft.IconButton(
            ft.Icons.CLOSE,
            icon_color=ft.Colors.RED_400,
            icon_size=20,
            tooltip="حذف سطح",
            on_click=lambda e: _remove_row(levels_column, row_wrap, app),
        )

        row_inner = ft.ResponsiveRow([
            ft.Column([title_field], col={"xs": 12, "sm": 6}),
            ft.Column([score_field], col={"xs": 6, "sm": 2}),
            ft.Column([color_dd], col={"xs": 5, "sm": 3}),
            ft.Column([preview], col={"xs": 1, "sm": 1}),
        ], spacing=8, run_spacing=8)

        row_wrap = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=8,
                            color=ft.Colors.GREY_400),
                    ft.Text("سطح وظیفه", size=11,
                            color=ft.Colors.GREY_600,
                            weight=ft.FontWeight.W_500),
                    ft.Container(expand=True),
                    remove_btn,
                ], spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                row_inner,
            ], spacing=6),
            padding=12,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=14,
            border=ft.Border.all(
                1, ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY)),
            shadow=ft.BoxShadow(
                blur_radius=6, spread_radius=0,
                color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )
        row_wrap.data = {
            "title": title_field,
            "score": score_field,
            "color": color_dd,
        }
        return row_wrap

    def add_level_row(e=None):
        if len(levels_column.controls) >= 10:
            app.snack("حداکثر ۱۰ سطح مجاز است")
            return
        levels_column.controls.append(make_level_row())
        page.update()

    # سه سطح پیش‌فرض
    levels_column.controls.append(
        make_level_row(score="1", color="#2E7D32"))
    levels_column.controls.append(
        make_level_row(score="2", color="#4CAF50"))
    levels_column.controls.append(
        make_level_row(score="3", color="#8BC34A"))

    # ---------- ثبت فرم ----------
    async def submit(e):
        name = name_field.value.strip()
        if not name:
            app.snack("نام چله را وارد کنید")
            return

        levels = []
        for row_wrap in levels_column.controls:
            t = row_wrap.data["title"].value.strip()
            try:
                s = int(row_wrap.data["score"].value or 0)
            except ValueError:
                app.snack("امتیاز باید عدد باشد")
                return
            col = row_wrap.data["color"].value or "#4CAF50"
            if not t:
                app.snack("عنوان همه سطوح را وارد کنید")
                return
            if s < 0:
                app.snack("امتیاز نمی‌تواند منفی باشد")
                return
            levels.append({"title": t, "score": s, "color": col})

        if len(levels) < 2:
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
    # بخش اطلاعات پایه
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

    # بخش سطوح
    levels_section = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LAYERS_OUTLINED, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("سطوح وظیفه", size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.TextButton(
                    "افزودن سطح",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    on_click=add_level_row,
                ),
            ], spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=14,
                            color=ft.Colors.AMBER_700),
                    ft.Text(
                        "هر سطح شامل عنوان، امتیاز و رنگ است. "
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

    # بخش تاریخ شروع
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

    # دکمه‌های پایین
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

    # ---------- ساختار نهایی ----------
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


# ---------- توابع کمکی ----------
def _remove_row(levels_column: ft.Column, row_wrap: ft.Container, app):
    if len(levels_column.controls) <= 2:
        app.snack("حداقل دو سطح لازم است")
        return
    levels_column.controls.remove(row_wrap)
    app.page.update()