from datetime import date, timedelta
import flet as ft

from utils import to_jalali, readable_text_color, to_persian_digits, get_unrecorded_days


# ---------- ابزار تشخیص دسکتاپ ----------
def _is_desktop(app) -> bool:
    page = getattr(app, "page", None)
    try:
        return bool(page and page.width and page.width >= 900)
    except Exception:
        return False


def build_status_view(app) -> ft.Control:
    c = app.current_chelleh
    if not c:
        return ft.Container(
            content=ft.Text("چله‌ای انتخاب نشده"),
            padding=40,
        )

    prog = c.progress()
    is_done = c.status == "completed"
    desktop = _is_desktop(app)

    # ---------- بخش‌ها ----------
    summary = _build_summary_card(c, prog, is_done, desktop)
    grid = _build_day_grid(app, c, desktop)
    history = _build_history_section(c, desktop)

    if app.current_chelleh and get_unrecorded_days(app.current_chelleh):
        app.navigate("/catchup")

    # ---------- بخش روزها ----------
    days_section = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.CALENDAR_VIEW_WEEK, size=18, color=ft.Colors.PRIMARY),
                    ft.Text("روزها", size=15 if desktop else 14, weight=ft.FontWeight.BOLD),
                ],
                spacing=8,
            ),
            ft.Text(
                "برای ثبت یادداشت و وضعیت، روی هر روز کلیک کنید",
                size=11,
                color=ft.Colors.GREY_600,
            ),
            ft.Container(height=8),
            grid,
        ],
        spacing=6,
    )

    # ---------- چیدمان واکنش‌گرا ----------
    # موبایل: همه بخش‌ها زیر هم (col=12)
    # دسکتاپ: «روزها» و «تاریخچه» کنار هم
    body_children = [ft.Container(summary, col=12)]

    if history:
        body_children += [
            ft.Container(days_section, col={"xs": 12, "md": 7, "lg": 8}),
            ft.Container(history, col={"xs": 12, "md": 5, "lg": 4}),
        ]
    else:
        body_children.append(ft.Container(days_section, col=12))

    body = ft.ResponsiveRow(body_children, spacing=20, run_spacing=20)

    return ft.Column(
        [
            ft.Container(
                content=body,
                padding=ft.Padding(
                    left=40 if desktop else 16,
                    right=40 if desktop else 16,
                    top=24 if desktop else 16,
                    bottom=32 if desktop else 24,
                ),
            ),
        ],
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


# ---------- کارت خلاصه ----------
def _build_summary_card(c, prog, is_done, desktop=False) -> ft.Container:
    ratio = prog / c.total_days if c.total_days else 0

    if is_done:
        status_label = "تکمیل شده ✅"
        status_color = "#2E7D32"
    else:
        current_day = to_persian_digits(str(c.current_day))
        total_days = to_persian_digits(str(c.total_days))
        status_label = f"روز {current_day} از {total_days}"
        status_color = ft.Colors.PRIMARY

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    c.display_name,
                                    size=18 if desktop else 16,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    c.name,
                                    size=12 if desktop else 11,
                                    color=ft.Colors.GREY_600,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text(
                                status_label,
                                size=11 if desktop else 10,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                            ),
                            padding=ft.Padding.symmetric(
                                vertical=6, horizontal=14 if desktop else 12
                            ),
                            bgcolor=status_color,
                            border_radius=10,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                ft.Row(
                    [
                        ft.Text(
                            f"{to_persian_digits(str(prog))} روز موفق",
                            size=12 if desktop else 11,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            f"دوره {to_persian_digits(str(c.cycle_number))}",
                            size=12 if desktop else 11,
                            color=ft.Colors.GREY_600,
                        ),
                    ]
                ),
                ft.Container(height=4),
                ft.ProgressBar(
                    value=ratio,
                    color=ft.Colors.PRIMARY,
                    bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY),
                    height=8,
                    border_radius=4,
                ),
            ]
        ),
        padding=20 if desktop else 16,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=10, spread_radius=0,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 3),
        ),
    )


# ---------- شبکه روزها ----------
def _build_day_grid(app, c, desktop=False) -> ft.Control:
    cells = []
    start = date.fromisoformat(c.cycle_start_date)
    for i in range(1, c.total_days + 1):
        day_date = to_jalali(start + timedelta(days=i - 1))
        cells.append(_make_day_cell(app, c, i, day_date, desktop))
    return ft.ResponsiveRow(cells, spacing=6, run_spacing=6)


def _make_day_cell(app, c, i, day_date, desktop=False) -> ft.Container:
    rec = c.daily_logs.get(str(i), {})
    result = rec.get("result")
    is_current = (i == c.current_day) and (c.status == "active")
    is_future = i > c.current_day
    is_clickable = not is_future

    # ---------- رنگ و متن ----------
    if result == "success":
        li = rec.get("level_index", 0)
        if 0 <= li < len(c.levels):
            bg = c.levels[li]["color"]
            fg = readable_text_color(bg)
        else:
            bg, fg = "#2E7D32", ft.Colors.WHITE
        border = None
    elif result == "failure":
        bg, fg = "#C62828", ft.Colors.WHITE
        border = None
    elif is_current:
        bg = ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY)
        fg = ft.Colors.PRIMARY
        border = ft.Border.all(2, ft.Colors.PRIMARY)
    elif is_future:
        bg = ft.Colors.with_opacity(0.05, ft.Colors.GREY)
        fg = ft.Colors.GREY_400
        border = None
    else:
        bg = ft.Colors.with_opacity(0.08, ft.Colors.GREY)
        fg = ft.Colors.GREY_500
        border = None

    # ---------- محتوای سلول ----------
    cell_children = [
        ft.Text(to_persian_digits(str(i)), size=13, weight=ft.FontWeight.BOLD, color=fg),
        ft.Text(to_persian_digits(day_date), size=10),
    ]

    if result == "success":
        cell_children.append(ft.Icon(ft.Icons.CHECK, size=10, color=fg))
    elif result == "failure":
        cell_children.append(ft.Icon(ft.Icons.CLOSE, size=10, color=fg))
    else:
        cell_children.append(ft.Container(height=10))

    def on_click(e):
        if not is_clickable:
            return
        app.selected_day = i
        app.navigate("/day")

    return ft.Container(
        content=ft.Column(
            cell_children,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        height=52 if desktop else 48,
        bgcolor=bg,
        border=border,
        border_radius=10,
        alignment=ft.Alignment.CENTER,
        ink=is_clickable,
        on_click=on_click if is_clickable else None,
        # موبایل: ۴ سلول در ردیف | تبلت: ۶ | لپ‌تاپ/دسکتاپ: ۸
        col={"xs": 3, "sm": 2, "md": 2, "lg": 1.5, "xl": 1.5},
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )


# ---------- تاریخچه (بخش جدا) ----------
def _build_history_section(c, desktop=False) -> ft.Control | None:
    if not c.history:
        return None

    rows = []
    for h in reversed(c.history):
        is_success = h["status"] == "completed"
        status_text = "موفق" if is_success else "شکست"
        status_color = "#2E7D32" if is_success else "#C62828"

        rows.append(
            ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.CHECK if is_success else ft.Icons.CLOSE,
                                size=18, color=ft.Colors.WHITE,
                            ),
                            width=36, height=36,
                            bgcolor=status_color,
                            border_radius=18,
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Text(
                                            f"دوره {h['cycle']}",
                                            size=13 if desktop else 12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Container(
                                            content=ft.Text(
                                                status_text,
                                                size=9,
                                                color=ft.Colors.WHITE,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            padding=ft.Padding.symmetric(
                                                vertical=2, horizontal=8
                                            ),
                                            bgcolor=status_color,
                                            border_radius=6,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                ft.Text(
                                    f"{to_jalali(date.fromisoformat(h['start_date']))} ← "
                                    f"{to_jalali(date.fromisoformat(h['end_date']))}",
                                    size=10, color=ft.Colors.GREY_600,
                                ),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Text(
                            f"{h['days_completed']} روز",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=status_color,
                        ),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=12 if desktop else 10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border_radius=12,
            )
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.HISTORY, size=18, color=ft.Colors.PRIMARY),
                        ft.Text(
                            "تاریخچه دوره‌ها",
                            size=15 if desktop else 14,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(expand=True),
                        ft.Container(
                            content=ft.Text(
                                f"{to_persian_digits(len(c.history))} دوره",
                                size=10,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                            ),
                            padding=ft.Padding.symmetric(vertical=3, horizontal=10),
                            bgcolor=ft.Colors.PRIMARY,
                            border_radius=8,
                        ),
                    ],
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(height=10),
                ft.Column(rows, spacing=8),
            ],
            spacing=4,
        ),
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )