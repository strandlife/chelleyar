from datetime import date, timedelta

import flet as ft

from utils import (to_jalali, to_persian_digits, readable_text_color,
                  get_unrecorded_days)

FAILURE_COLOR = "#C62828"


def build_catchup_view(app) -> ft.Control:
    page = app.page
    c = app.current_cheleh
    if c is None:
        return ft.Container(content=ft.Text("چله‌ای انتخاب نشده"), padding=40)

    # صف هر بار از روی داده‌های واقعی محاسبه می‌شود
    pending = get_unrecorded_days(c)

    if not pending:
        return _all_done_view(app)

    day = pending[0]
    start = date.fromisoformat(c.cycle_start_date)
    day_jdate = to_persian_digits(to_jalali(start + timedelta(days=day - 1)))

    selected_level = 0

    # ---------- چیپ‌های سطح (شامل سطح شکست) ----------
    chips = []

    def render_chips():
        for j, ch in enumerate(chips):
            lv = c.levels[j]
            is_fail = (lv.get("score", 0) == 0)
            is_sel = (j == selected_level)
            ch.bgcolor = lv["color"] if is_sel else ft.Colors.SURFACE_CONTAINER_LOW
            ch.border = (None if is_sel
                         else ft.Border.all(1, ft.Colors.with_opacity(0.35, lv["color"])))
            ch.content.controls[1].color = (
                readable_text_color(lv["color"]) if is_sel
                else (FAILURE_COLOR if is_fail else ft.Colors.GREY_700)
            )

    def pick_level(e, idx: int):
        nonlocal selected_level
        selected_level = idx
        render_chips()
        page.update()

    for idx, lv in enumerate(c.levels):
        is_fail = (lv.get("score", 0) == 0)
        label = (f"{lv['title']} ({to_persian_digits(str(lv['score']))} امتیاز)"
                 if not is_fail else f"✖ {lv['title']}")
        chips.append(ft.Container(
            content=ft.Row([
                ft.Container(width=10, height=10, bgcolor=lv["color"],
                             border_radius=5),
                ft.Text(label, size=11),
            ], spacing=5),
            padding=ft.Padding.symmetric(vertical=7, horizontal=12),
            border_radius=20,
            ink=True,
            on_click=lambda e, i=idx: pick_level(e, i),
        ))
    render_chips()

    # ---------- ثبت ----------
    def do_failure():
        app.fail_chelleh(c)
        app.snack("چله شکست خورد — دوره جدید از امروز شروع شد")
        app.navigate("/status")

    def confirm_failure():
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.RED, size=26),
                ft.Text("هشدار شکست چله", weight=ft.FontWeight.BOLD),
            ]),
            content=ft.Text(
                "با ثبت سطح «شکست»، این چله شکست خورده و دوره جدید "
                "از امروز شروع می‌شود.\n\nآیا مطمئن هستید؟",
                size=13,
            ),
            actions=[
                ft.TextButton("انصراف", on_click=lambda e: page.pop_dialog()),
                ft.Button(
                    "بله، شکست خورد",
                    on_click=lambda e: (page.pop_dialog(), do_failure()),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.RED,
                                         color=ft.Colors.WHITE),
                ),
            ],
        )
        page.show_dialog(dialog)

    def submit(e):
        lv = c.levels[selected_level]

        if lv.get("score", 0) == 0:          # سطح شکست انتخاب شده
            confirm_failure()
            return

        # موفقیت با سطح انتخابی
        rec = c.daily_logs.setdefault(str(day), {})
        rec["result"] = "success"
        rec["level_index"] = selected_level
        rec["score"] = lv["score"]
        rec["date"] = date.today().isoformat()
        app.db.save_cheleh(c)
        app.refresh()                         # روز بعدی خودش محاسبه می‌شود

    submit_btn = ft.Button(
        "ثبت",
        icon=ft.Icons.CHECK_CIRCLE,
        on_click=submit,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.PRIMARY, color=ft.Colors.WHITE,
            padding=ft.Padding.symmetric(vertical=14, horizontal=32),
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=18, color=ft.Colors.PRIMARY),
                ft.Text("تکمیل روزهای عقب‌افتاده", size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Text(f"{to_persian_digits(str(len(pending)))} روز باقی‌مانده",
                        size=11, color=ft.Colors.GREY_600),
            ], spacing=8),
            ft.Container(height=14),
            ft.Container(
                content=ft.Column([
                    ft.Text(f"روز {to_persian_digits(str(day))}", size=22,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(day_jdate, size=13, color=ft.Colors.GREY_600),
                    ft.Container(height=10),
                    ft.Text("سطح عملکرد این روز را انتخاب کنید", size=13),
                    ft.Row(chips, spacing=6, wrap=True, run_spacing=6,
                           alignment=ft.MainAxisAlignment.CENTER),
                    ft.Container(height=14),
                    submit_btn,
                    ft.TextButton("فعلاً بی‌خیال، بعداً تصمیم می‌گیرم",
                                  on_click=lambda e: app.navigate("/status")),
                ], spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20, border_radius=16,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                shadow=ft.BoxShadow(blur_radius=10, spread_radius=0,
                                    color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                                    offset=ft.Offset(0, 3)),
            ),
        ], spacing=8),
        padding=16,
    )


def _all_done_view(app) -> ft.Control:
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.TASK_ALT, size=56, color="#2E7D32"),
            ft.Text("روز عقب‌افتاده‌ای برای تعیین تکلیف وجود ندارد",
                    size=15, weight=ft.FontWeight.BOLD),
            ft.Text(
                "اگر روزی ثبت نشده باشد، دفعه بعد که برنامه را باز کنید "
                "از شما پرسیده می‌شود.",
                size=11, color=ft.Colors.GREY_600,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Button("بازگشت به چله",
                      on_click=lambda e: app.navigate("/status")),
        ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=60,
    )