from datetime import date

import flet as ft
import uuid
from theme import elevated_card
from utils import to_jalali, to_persian_digits

MAX_LEVELS = 10
MIN_LEVELS = 2

def _new_level_id() -> str:
    return str(uuid.uuid4())

def build_edit_view(app) -> ft.Control:
    page = app.page
    c = app.editing_chelleh

    # ---------- بررسی وجود چله ----------
    if not c:
        return ft.SafeArea(
            content=ft.Column([
                ft.Text("چله‌ای برای ویرایش انتخاب نشده"),
                ft.TextButton("بازگشت", on_click=lambda e: app.navigate("/")),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )

    has_history = bool(c.daily_logs) or bool(c.history)

    # ---------- فیلدهای اصلی (پیش‌پر شده) ----------
    name_field = ft.TextField(
        label="نام اصلی چله", value=c.name,
        hint_text="مثلاً: چله نماز صبح",
        border_radius=12, filled=True,
        prefix_icon=ft.Icons.LABEL_OUTLINED,
    )
    display_field = ft.TextField(
        label="نام نمایشی", value=c.display_name,
        hint_text="در لیست چله‌ها نمایش داده می‌شود",
        border_radius=12, filled=True,
        prefix_icon=ft.Icons.VISIBILITY_OUTLINED,
    )
    task_field = ft.TextField(
        label="وظیفه‌ای که باید مراقبت شود", value=c.task,
        hint_text="مثلاً: خواندن نماز صبح در اول وقت",
        multiline=True, min_lines=2,
        border_radius=12, filled=True,
        prefix_icon=ft.Icons.TASK_ALT_OUTLINED,
    )

    # ---------- سطوح (کپی کاری — انصراف برگرداندنی است) ----------
    levels: list[dict] = [dict(lv) for lv in (c.levels or [])]
    levels_column = ft.Column(spacing=8)
    levels_counter = ft.Text(size=11, color=ft.Colors.GREY_500)

    # ---------- دیالوگ افزودن / ویرایش سطح ----------
    def open_level_dialog(e=None, index: int | None = None):
        is_edit = index is not None
        initial = dict(levels[index]) if is_edit else {
            "title": "", "score": "", "color": "#4CAF50"}

        title_field = ft.TextField(
            label="عنوان سطح", value=initial["title"],
            hint_text="مثلاً: نماز صبح اول وقت",
            border_radius=10, filled=True, autofocus=True,
            prefix_icon=ft.Icons.LABEL_OUTLINE,
        )
        score_field = ft.TextField(
            label="امتیاز", value=str(initial["score"]),
            hint_text="عدد مثبت؛ مثلاً 5",
            border_radius=10, filled=True,
            keyboard_type=ft.KeyboardType.NUMBER,
            prefix_icon=ft.Icons.STAR_OUTLINE,
        )
        color_dd = ft.Dropdown(
            label="رنگ", value=initial["color"],
            border_radius=10, filled=True,
            options=[ft.DropdownOption(key=k, text=t)
                     for k, t in __import__("utils").COLOR_OPTIONS],
        )
        preview = ft.Container(
            width=36, height=36, bgcolor=initial["color"],
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
                page.update(); return
            raw = (score_field.value or "").strip()
            if not raw:
                score_field.error_text = "امتیاز را وارد کنید"
                page.update(); return
            try:
                s = int(raw)
            except ValueError:
                score_field.error_text = "امتیاز باید عدد باشد"
                page.update(); return
            if s < 0:
                score_field.error_text = "امتیاز نمی‌تواند منفی باشد"
                page.update(); return
            if any(lv["score"] == s
                   for i_lv, lv in enumerate(levels) if i_lv != index):
                score_field.error_text = "این امتیاز قبلاً استفاده شده است"
                page.update(); return

            data = {"title": t, "score": s,
                    "color": color_dd.value or "#4CAF50"}
            if is_edit:
                levels[index] = data
            else:
                levels.append(data)
            refresh_levels()
            page.pop_dialog()

        score_field.on_submit = save

        page.show_dialog(ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.LAYERS_OUTLINED, size=20,
                        color=ft.Colors.PRIMARY),
                ft.Text("ویرایش سطح" if is_edit else "افزودن سطح",
                        size=16, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            content=ft.Column([
                title_field, score_field,
                ft.Row([
                    ft.Container(content=color_dd, expand=True), preview,
                ], spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ], tight=True, spacing=12),
            actions=[
                ft.TextButton("انصراف", on_click=lambda e: page.pop_dialog()),
                ft.Button("ذخیره", icon=ft.Icons.CHECK, on_click=save,
                          style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY,
                                               color=ft.Colors.WHITE)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        ))

    # ---------- نمایش خلاصه سطوح ----------
    def make_level_tile(index: int, lv: dict) -> ft.Container:
        is_system = int(lv.get("score", 0)) == 0
        sys_tip = "سطح شکست سیستمی است و قابل تغییر نیست"
        score_chip = ft.Container(
            content=ft.Text(f"امتیاز {to_persian_digits(str(lv['score']))}",
                            size=11, weight=ft.FontWeight.BOLD, color=lv["color"]),
            bgcolor=ft.Colors.with_opacity(0.12, lv["color"]),
            padding=ft.Padding.symmetric(horizontal=8, vertical=4),
            border_radius=20,
        )
        return ft.Container(
            content=ft.Row([
                ft.Container(width=14, height=14, bgcolor=lv["color"],
                             border_radius=7,
                             border=ft.Border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.BLACK))),
                ft.Text(lv["title"] or "بدون عنوان", size=13,
                        weight=ft.FontWeight.W_600, expand=True,
                        italic=not lv["title"],
                        color=ft.Colors.GREY_500 if not lv["title"] else None),
                score_chip,
                ft.IconButton(ft.Icons.EDIT_OUTLINED, icon_size=18,
                              tooltip=sys_tip if is_system else "ویرایش سطح",
                              icon_color=ft.Colors.GREY_700,
                              disabled=is_system,
                              on_click=lambda e, i=index: open_level_dialog(index=i)),
                ft.IconButton(ft.Icons.DELETE_OUTLINE, icon_size=18,
                              tooltip=sys_tip if is_system else "حذف سطح",
                              icon_color=ft.Colors.RED_400,
                              disabled=is_system,
                              on_click=lambda e, i=index: remove_level(i)),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY)),
        )

    def refresh_levels():
        levels_column.controls.clear()
        for i, lv in enumerate(levels):
            levels_column.controls.append(make_level_tile(i, lv))
        levels_counter.value = (
            f"{to_persian_digits(str(len(levels)))} از "
            f"{to_persian_digits(str(MAX_LEVELS))} سطح"
        )
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

    # ---------- هشدار وابستگی تاریخچه به ترتیب سطوح ----------
    history_warning = None
    if has_history:
        history_warning = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=14, color=ft.Colors.DEEP_ORANGE_700),
                ft.Text(
                    "این چله سابقه ثبت‌شده دارد. آمار روزهای گذشته به "
                    "ترتیب سطوح وابسته است؛ از حذف سطوح خودداری کنید.",
                    size=11, color=ft.Colors.GREY_600, expand=True),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.START),
            padding=ft.Padding.symmetric(vertical=8, horizontal=10),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.DEEP_ORANGE),
            border_radius=10,
        )

    # ---------- بخش وضعیت فعلی ----------
    info_section = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.HISTORY_TOGGLE_OFF, size=18, color=ft.Colors.PRIMARY),
                ft.Text("وضعیت فعلی", size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=4),
            ft.ResponsiveRow([
                ft.Column([_info_chip(ft.Icons.REPEAT, "دوره",
                                      to_persian_digits(str(c.cycle_number)),
                                      ft.Colors.BLUE)],
                          col={"xs": 12, "sm": 4}),
                ft.Column([_info_chip(ft.Icons.CALENDAR_TODAY, "روز فعلی",
                                      f"{to_persian_digits(str(c.current_day))} از "
                                      f"{to_persian_digits(str(c.total_days))}",
                                      ft.Colors.GREEN)],
                          col={"xs": 12, "sm": 4}),
                ft.Column([_info_chip(ft.Icons.CHECK_CIRCLE_OUTLINE, "موفق",
                                      to_persian_digits(str(c.progress())),
                                      ft.Colors.ORANGE)],
                          col={"xs": 12, "sm": 4}),
            ], spacing=8, run_spacing=8),
        ], spacing=8),
        padding=16,
    )

    # ---------- بخش اطلاعات پایه ----------
    basic_info = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18, color=ft.Colors.PRIMARY),
                ft.Text("اطلاعات پایه", size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=4),
            ft.ResponsiveRow([
                ft.Column([name_field], col={"xs": 12, "md": 6}),
                ft.Column([display_field], col={"xs": 12, "md": 6}),
            ], spacing=10, run_spacing=10),
            task_field,
        ], spacing=10),
        padding=16,
    )

    # ---------- بخش سطوح ----------
    levels_children = [
        ft.Row([
            ft.Icon(ft.Icons.LAYERS_OUTLINED, size=18, color=ft.Colors.PRIMARY),
            ft.Text("سطوح وظیفه", size=14, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            levels_counter,
            ft.TextButton("افزودن سطح",
                          icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                          on_click=add_level_click),
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        history_warning,
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=14, color=ft.Colors.AMBER_700),
                ft.Text("سطح «شکست» (امتیاز صفر) سیستمی است و قابل ویرایش یا حذف نیست.",
                        size=11, color=ft.Colors.GREY_600),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.START),
            padding=ft.Padding.symmetric(vertical=8, horizontal=10),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.AMBER),
            border_radius=10,
        ),
        levels_column,
    ]
    levels_section = elevated_card(
        ft.Column([x for x in levels_children if x is not None], spacing=12),
        padding=16,
    )

    # ---------- تاریخ شروع (فقط نمایش) ----------
    date_section = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, size=18, color=ft.Colors.PRIMARY),
                ft.Text("تاریخ شروع", size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.EVENT_AVAILABLE,
                                        color=ft.Colors.GREEN_700, size=22),
                        padding=8,
                        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREEN),
                        border_radius=10,
                    ),
                    ft.Column([
                        ft.Text("تاریخ شروع چله", size=10, color=ft.Colors.GREY_600),
                        ft.Text(to_jalali(date.fromisoformat(c.cycle_start_date)),
                                size=13, weight=ft.FontWeight.BOLD),
                    ], spacing=0, expand=True),
                    ft.Text("غیرقابل تغییر", size=10, color=ft.Colors.GREY_500),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.Padding.symmetric(vertical=8, horizontal=10),
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border_radius=12,
            ),
            ft.Text(
                "تاریخ شروع پس از ساخت چله تغییر نمی‌کند تا تاریخ روزهای "
                "ثبت‌شده با خط‌زمانی چله هماهنگ بماند.",
                size=10, color=ft.Colors.GREY_500),
        ], spacing=8),
        padding=16,
    )

    # ---------- ثبت ----------
    async def submit(e):
        name = name_field.value.strip()
        if not name:
            app.snack("نام چله را وارد کنید"); return
        if any(not (lv["title"] or "").strip() for lv in levels):
            app.snack("عنوان همه سطوح را وارد کنید"); return
        if len(levels) < MIN_LEVELS:
            app.snack("حداقل دو سطح وظیفه تعریف کنید"); return
        if not any(lv["score"] == 0 for lv in levels):
            levels.append({"id": _new_level_id(),"title": "شکست", "score": 0, "color": "#C62828"})

        c.name = name
        c.display_name = display_field.value.strip() or name
        c.task = task_field.value.strip()
        c.levels = levels
        app.db.save_chelleh(c)
        app.snack("تغییرات با موفقیت ذخیره شد ✅")
        app.editing_chelleh = None
        await page.push_route("/")

    def cancel(e):
        app.editing_chelleh = None
        app.navigate("/")

    # ---------- دکمه‌ها ----------
    cancel_btn = ft.TextButton("انصراف", icon=ft.Icons.CLOSE, on_click=cancel,
                               style=ft.ButtonStyle(color=ft.Colors.GREY_600))
    submit_btn = ft.Button(
        "ذخیره تغییرات", icon=ft.Icons.SAVE_OUTLINED, on_click=submit,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE,
            padding=ft.Padding.symmetric(vertical=14, horizontal=28),
            shape=ft.RoundedRectangleBorder(radius=12), elevation=2,
        ),
    )
    actions = (
        ft.Row([cancel_btn, ft.Container(expand=True), submit_btn],
               spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        if app.is_desktop()
        else ft.Column([submit_btn,
                        ft.Row([cancel_btn], alignment=ft.MainAxisAlignment.CENTER)],
                       spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # ---------- ساختار نهایی ----------
    return ft.Column([
        ft.Container(
            content=ft.Column([
                info_section,
                basic_info,
                levels_section,
                date_section,
                actions,
                ft.Container(height=24),
            ], spacing=14),
            padding=ft.Padding.only(left=16, right=16, top=16, bottom=8),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)


def _info_chip(icon, label: str, value: str, color) -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=14, color=color),
            ft.Column([
                ft.Text(label, size=9, color=ft.Colors.GREY_600),
                ft.Text(value, size=12, weight=ft.FontWeight.BOLD, color=color),
            ], spacing=0, expand=True),
        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=8, horizontal=12),
        bgcolor=ft.Colors.with_opacity(0.08, color),
        border_radius=10,
    )