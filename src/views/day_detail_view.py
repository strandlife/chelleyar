from datetime import date
import flet as ft

from utils import to_jalali, readable_text_color


def build_day_detail_view(app) -> ft.Control:
    page = app.page
    c = app.current_cheleh

    if not c or not app.selected_day:
        return _error_view(app, "روز انتخاب نشده")

    day = app.selected_day
    if day < 1 or day > c.total_days:
        return _error_view(app, "شماره روز نامعتبر است")

    is_editable = (day == c.current_day) and (c.status == "active")

    # دریافت یا ساخت لاگ
    key = str(day)
    if key not in c.daily_logs:
        c.daily_logs[key] = {
            "morning_note": "",
            "evening_note": "",
            "level_index": 0,
            "score": 0,
            "result": None,
            "morning_saved": False,
            "evening_saved": False,
            "date": date.today().isoformat(),
        }
    log = c.daily_logs[key]

    # ---------- هدر خلاصه روز ----------
    day_header = _build_day_header(c, day, log, is_editable)

    # ---------- حالت فقط-خواندنی برای روزهای گذشته ----------
    if not is_editable:
        return _read_only_view(app, c, day, log, day_header)

    # ---------- حالت قابل ویرایش (روز جاری) ----------
    return _editable_view(app, c, day, log, day_header)


# ---------- هدر روز ----------
def _build_day_header(c, day, log, is_editable) -> ft.Container:
    result = log.get("result")
    if result == "success":
        badge_text = "موفق"
        badge_color = "#2E7D32"
    elif result == "failure":
        badge_text = "شکست"
        badge_color = "#C62828"
    elif is_editable:
        badge_text = "امروز"
        badge_color = ft.Colors.PRIMARY
    else:
        badge_text = "بدون ثبت"
        badge_color = ft.Colors.GREY_500

    # تاریخ تقریبی
    try:
        start = date.fromisoformat(c.cycle_start_date)
        day_date = start + __import__("datetime").timedelta(days=day - 1)
        date_str = to_jalali(day_date)
    except Exception:
        date_str = ""

    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Text(str(day), size=22,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE),
                width=60, height=60,
                bgcolor=badge_color,
                border_radius=30,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column([
                ft.Text(f"روز {day} از {c.total_days}", size=15,
                        weight=ft.FontWeight.BOLD),
                ft.Text(date_str, size=11, color=ft.Colors.GREY_600),
                ft.Container(
                    content=ft.Text(badge_text, size=10,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                    padding=ft.Padding.symmetric(vertical=3, horizontal=10),
                    bgcolor=badge_color,
                    border_radius=8,
                ),
            ], spacing=4, expand=True),
        ], spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 3),
        ),
    )


# ---------- حالت قابل ویرایش ----------
def _editable_view(app, c, day, log, day_header) -> ft.Control:
    page = app.page

    # ---------- یادداشت صبح ----------
    morning_note = ft.TextField(
        label="یادداشت صبح",
        multiline=True, min_lines=3, max_lines=6,
        value=log.get("morning_note", ""),
        hint_text="قبل از شروع روز چه قصدی دارید؟",
        border_radius=12,
        filled=True,
    )

    async def save_morning(e):
        log["morning_note"] = morning_note.value
        log["morning_saved"] = True
        app.db.save_cheleh(c)
        app.snack("یادداشت صبح ذخیره شد ☀️")
        _refresh(app)

    morning_card = _note_card(
        icon=ft.Icons.WB_SUNNY,
        title="شروع روز",
        subtitle="قبل از شروع، قصد خود را بنویسید",
        color="#FF9800",
        note_field=morning_note,
        save_btn=ft.Button(
            "ذخیره یادداشت صبح",
            icon=ft.Icons.SAVE_OUTLINED,
            on_click=save_morning,
            style=ft.ButtonStyle(
                bgcolor="#FF9800", color=ft.Colors.WHITE,
                padding=ft.Padding.symmetric(vertical=10, horizontal=16),
            ),
        ),
        is_saved=log.get("morning_saved", False),
    )

    # ---------- یادداشت پایان روز ----------
    evening_note = ft.TextField(
        label="یادداشت پایان روز",
        multiline=True, min_lines=3, max_lines=6,
        value=log.get("evening_note", ""),
        hint_text="امروز چطور گذشت؟",
        border_radius=12,
        filled=True,
    )

    async def save_evening(e):
        log["evening_note"] = evening_note.value
        log["evening_saved"] = True
        app.db.save_cheleh(c)
        app.snack("یادداشت پایان روز ذخیره شد 🌙")
        _refresh(app)

    evening_card = _note_card(
        icon=ft.Icons.NIGHTLIGHT,
        title="پایان روز",
        subtitle="امروز چطور گذشت؟",
        color="#3F51B5",
        note_field=evening_note,
        save_btn=ft.Button(
            "ذخیره یادداشت پایان روز",
            icon=ft.Icons.SAVE_OUTLINED,
            on_click=save_evening,
            style=ft.ButtonStyle(
                bgcolor="#3F51B5", color=ft.Colors.WHITE,
                padding=ft.Padding.symmetric(vertical=10, horizontal=16),
            ),
        ),
        is_saved=log.get("evening_saved", False),
    )

    # ---------- انتخاب سطح ----------
    current_level = log.get("level_index", 0)
    if not (0 <= current_level < len(c.levels)):
        current_level = 0

    level_dd = ft.Dropdown(
        label="سطح وظیفه امروز",
        value=str(current_level),
        border_radius=12,
        filled=True,
        options=[
            ft.DropdownOption(
                key=str(i),
                text=f"{lv['title']} ({lv['score']} امتیاز)",
            )
            for i, lv in enumerate(c.levels)
        ],
    )

    submit_btn = ft.Button(
        "ثبت وضعیت و بازگشت",
        icon=ft.Icons.CHECK_CIRCLE,
        on_click=lambda e: _submit_day(app, c, log, level_dd, submit_btn),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY,
            color=ft.Colors.WHITE,
            padding=ft.Padding.symmetric(vertical=14, horizontal=24),
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation=2,
        ),
    )

    status_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.RULE, size=18, color=ft.Colors.PRIMARY),
                ft.Text("وضعیت امروز", size=14,
                        weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=4),
            level_dd,
            ft.Container(height=8),
            submit_btn,
        ], spacing=8),
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    return ft.Column([
        ft.Container(
            content=ft.Column([
                day_header,
                ft.Container(height=14),
                morning_card,
                ft.Container(height=12),
                evening_card,
                ft.Container(height=14),
                status_card,
                ft.Container(height=24),
            ], spacing=0),
            padding=ft.Padding.symmetric(vertical=16, horizontal=16),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)


# ---------- حالت فقط خواندنی ----------
def _read_only_view(app, c, day, log, day_header) -> ft.Control:
    result = log.get("result")

    # سطح انتخاب‌شده
    level_info = None
    if result == "success":
        li = log.get("level_index", 0)
        if 0 <= li < len(c.levels):
            level_info = c.levels[li]

    # ---------- ساخت لیست کنترل‌ها به‌صورت جداگانه ----------
    detail_children = [
        ft.Row([
            ft.Icon(ft.Icons.INFO_OUTLINE, size=18,
                    color=ft.Colors.PRIMARY),
            ft.Text("جزئیات این روز", size=14,
                    weight=ft.FontWeight.BOLD),
        ], spacing=8),
        ft.Container(height=8),
    ]

    if result == "failure":
        detail_children.append(
            _read_row(ft.Icons.CLOSE, "نتیجه",
                      "این روز با شکست ثبت شده",
                      "#C62828")
        )
    elif level_info:
        detail_children.append(
            _read_row(ft.Icons.STAR, "سطح انتخاب‌شده",
                      f"{level_info['title']} "
                      f"({level_info['score']} امتیاز)",
                      level_info["color"])
        )
    else:
        detail_children.append(
            _read_row(ft.Icons.REMOVE_CIRCLE_OUTLINE, "وضعیت",
                      "این روز ثبت نشده", ft.Colors.GREY_500)
        )

    detail_children.append(ft.Container(height=8))

    if log.get("morning_note"):
        detail_children.append(
            _read_note(ft.Icons.WB_SUNNY, "یادداشت صبح",
                       log["morning_note"], "#FF9800")
        )
    if log.get("evening_note"):
        detail_children.append(
            _read_note(ft.Icons.NIGHTLIGHT, "یادداشت پایان روز",
                       log["evening_note"], "#3F51B5")
        )

    detail_card = ft.Container(
        content=ft.Column(detail_children, spacing=6),
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )

    return ft.Column([
        ft.Container(
            content=ft.Column([
                day_header,
                ft.Container(height=14),
                detail_card,
                ft.Container(height=24),
            ]),
            padding=ft.Padding.symmetric(vertical=16, horizontal=16),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)


def _read_row(icon, label, value, color) -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(icon, size=16, color=color),
                width=32, height=32,
                bgcolor=ft.Colors.with_opacity(0.12, color),
                border_radius=8,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column([
                ft.Text(label, size=10, color=ft.Colors.GREY_600),
                ft.Text(value, size=12, weight=ft.FontWeight.W_500),
            ], spacing=0, expand=True),
        ], spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=8,
    )


def _read_note(icon, label, text, color) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, size=14, color=color),
                ft.Text(label, size=11, color=color,
                        weight=ft.FontWeight.BOLD),
            ], spacing=6),
            ft.Container(
                content=ft.Text(text, size=12),
                padding=10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                border_radius=8,
            ),
        ], spacing=6),
        padding=ft.Padding.only(top=6),
    )


# ---------- ثبت وضعیت روز ----------
def _submit_day(app, c, log, level_dd, submit_btn):
    page = app.page

    li = int(level_dd.value or 0)
    if not (0 <= li < len(c.levels)):
        app.snack("سطح معتبر انتخاب کنید")
        return

    selected = c.levels[li]
    score = selected["score"]

    if score == 0:
        _show_failure_dialog(app, c, log, li)
    else:
        _record_success(app, c, log, li, score)


def _record_success(app, c, log, li, score):
    log["level_index"] = li
    log["score"] = score
    log["result"] = "success"
    log["date"] = date.today().isoformat()

    if c.is_last_day():
        _show_completion_dialog(app, c)
    else:
        prev = c.current_day
        c.current_day += 1
        app.db.save_cheleh(c)
        app.snack(f"روز {prev} با موفقیت ثبت شد ✅")
        app.selected_day = None
        app.navigate("/status")


def _show_failure_dialog(app, c, log, li):
    page = app.page

    def do_failure():
        log["level_index"] = li
        log["score"] = 0
        log["result"] = "failure"
        log["date"] = date.today().isoformat()

        c.history.append({
            "cycle": c.cycle_number,
            "start_date": c.cycle_start_date,
            "end_date": date.today().isoformat(),
            "days_completed": c.progress(),
            "status": "failed",
        })
        c.cycle_number += 1
        c.cycle_start_date = date.today().isoformat()
        c.current_day = 1
        c.daily_logs = {}
        c.status = "active"

        app.db.save_cheleh(c)
        app.snack("چله شکست خورد و از ابتدا شروع شد")
        app.selected_day = None
        app.navigate("/status")

    def on_dismiss(e):
        if getattr(dialog, "_confirmed", False):
            do_failure()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.RED, size=26),
            ft.Text("هشدار شکست چله", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Text(
            "با انتخاب سطح «شکست»، این چله شکست خورده و از "
            "روز اول دوباره شروع می‌شود.\n\n"
            "آیا مطمئن هستید؟",
            size=13,
        ),
        actions=[
            ft.TextButton(
                "انصراف",
                on_click=lambda e: (setattr(dialog, "_confirmed", False),
                                    page.pop_dialog()),
            ),
            ft.Button(
                "بله، شکست خورد",
                on_click=lambda e: (setattr(dialog, "_confirmed", True),
                                    page.pop_dialog()),
                style=ft.ButtonStyle(bgcolor=ft.Colors.RED,
                                     color=ft.Colors.WHITE),
            ),
        ],
        on_dismiss=on_dismiss,
    )
    dialog._confirmed = False
    page.show_dialog(dialog)


def _show_completion_dialog(app, c):
    page = app.page
    action = {"value": None}

    def do_action():
        c.history.append({
            "cycle": c.cycle_number,
            "start_date": c.cycle_start_date,
            "end_date": date.today().isoformat(),
            "days_completed": c.total_days,
            "status": "completed",
        })
        if action["value"] == "renew":
            c.cycle_number += 1
            c.total_days += 40
            c.current_day += 1
            c.cycle_start_date = date.today().isoformat()
            app.db.save_cheleh(c)
            app.snack(f"چله تمدید شد! از روز {c.current_day} ادامه دهید 🎉")
        else:
            c.status = "completed"
            app.db.save_cheleh(c)
            app.snack("چله با موفقیت به پایان رسید 🎉")
        app.selected_day = None
        app.navigate("/status")

    def on_dismiss(e):
        if action["value"]:
            do_action()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.CELEBRATION, color=ft.Colors.GREEN, size=28),
            ft.Text("تبریک! چله کامل شد", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Text(
            f"شما {c.total_days} روز را با موفقیت گذراندید.\n\n"
            "آیا می‌خواهید چله را تمدید کنید (۴۰ روز دیگر) "
            "یا آن را به پایان برسانید؟",
            size=13,
        ),
        actions=[
            ft.TextButton(
                "پایان چله",
                on_click=lambda e: (action.update(value="finish"),
                                    page.pop_dialog()),
            ),
            ft.Button(
                "تمدید چله",
                on_click=lambda e: (action.update(value="renew"),
                                    page.pop_dialog()),
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN,
                                     color=ft.Colors.WHITE),
            ),
        ],
        on_dismiss=on_dismiss,
    )
    page.show_dialog(dialog)


# ---------- کارت یادداشت ----------
def _note_card(icon, title, subtitle, color,
               note_field, save_btn, is_saved) -> ft.Container:
    # ---------- ساخت لیست کنترل‌های هدر به‌صورت جداگانه ----------
    header_children = [
        ft.Container(
            content=ft.Icon(icon, color=color, size=20),
            padding=8,
            bgcolor=ft.Colors.with_opacity(0.15, color),
            border_radius=10,
        ),
        ft.Column([
            ft.Text(title, size=13, weight=ft.FontWeight.BOLD),
            ft.Text(subtitle, size=10, color=ft.Colors.GREY_600),
        ], spacing=0, expand=True),
    ]

    if is_saved:
        header_children.append(
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN,
                    size=20, tooltip="ذخیره شده")
        )

    header = ft.Row(
        header_children,
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    return ft.Container(
        content=ft.Column([
            header,
            note_field,
            ft.Row([save_btn], alignment=ft.MainAxisAlignment.END),
        ], spacing=10),
        padding=14,
        border_radius=14,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        border=ft.Border.all(
            1, ft.Colors.with_opacity(0.08, color)),
    )


# ---------- توابع کمکی ----------
def _error_view(app, msg):
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.ERROR_OUTLINE, size=48,
                    color=ft.Colors.GREY_400),
            ft.Text(msg, size=14, color=ft.Colors.GREY_600),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        alignment=ft.Alignment.CENTER, padding=40,
    )


def _refresh(app):
    """بازسازی صفحه جاری بدون تغییر مسیر"""
    app.route_change(None)