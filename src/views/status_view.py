from datetime import date
import flet as ft

from utils import to_jalali, readable_text_color


def build_status_view(app) -> ft.Control:
    c = app.current_cheleh
    if not c:
        return ft.Container(
            content=ft.Text("چله‌ای انتخاب نشده"),
            padding=40,
        )

    day_num = c.current_day
    prog = c.progress()
    is_done = c.status == "completed"

    # ---------- کارت خلاصه ----------
    summary = _build_summary_card(c, prog, is_done)

    # ---------- شبکه روزها ----------
    grid = _build_day_grid(app, c)

    # ---------- تاریخچه (جدا) ----------
    history = _build_history_section(c)

    # ---------- UI ----------
    return ft.Column([
        ft.Container(
            content=ft.Column([
                summary,
                ft.Container(height=16),

                # بخش روزها
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_VIEW_WEEK, size=18,
                            color=ft.Colors.PRIMARY),
                    ft.Text("روزها", size=14, weight=ft.FontWeight.BOLD),
                ], spacing=8),
                ft.Text(
                    "برای ثبت یادداشت و وضعیت، روی هر روز کلیک کنید",
                    size=11, color=ft.Colors.GREY_600),
                ft.Container(height=8),
                grid,

                ft.Container(height=20),

                # بخش تاریخچه (کاملاً جدا)
                history if history else ft.Container(),
            ], spacing=6),
            padding=ft.Padding.symmetric(vertical=16, horizontal=16),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)


# ---------- کارت خلاصه ----------
def _build_summary_card(c, prog, is_done) -> ft.Container:
    ratio = prog / c.total_days if c.total_days else 0

    if is_done:
        status_label = "تکمیل شده ✅"
        status_color = "#2E7D32"
    else:
        status_label = f"روز {c.current_day} از {c.total_days}"
        status_color = ft.Colors.PRIMARY

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text(c.display_name, size=16,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(c.name, size=11, color=ft.Colors.GREY_600),
                ], spacing=2, expand=True),
                ft.Container(
                    content=ft.Text(status_label, size=10,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                    padding=ft.Padding.symmetric(vertical=6, horizontal=12),
                    bgcolor=status_color,
                    border_radius=10,
                ),
            ], spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Row([
                ft.Text(f"{prog} روز موفق", size=11,
                        color=ft.Colors.GREY_600),
                ft.Container(expand=True),
                ft.Text(f"دوره {c.cycle_number}", size=11,
                        color=ft.Colors.GREY_600),
            ]),
            ft.Container(height=4),
            ft.ProgressBar(
                value=ratio,
                color=ft.Colors.PRIMARY,
                bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY),
                height=8, border_radius=4,
            ),
        ]),
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=10, spread_radius=0,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 3),
        ),
    )


# ---------- شبکه روزها ----------
def _build_day_grid(app, c) -> ft.Control:
    cells = []
    for i in range(1, c.total_days + 1):
        cells.append(_make_day_cell(app, c, i))
    return ft.ResponsiveRow(cells, spacing=6, run_spacing=6)


def _make_day_cell(app, c, i) -> ft.Container:
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

    # ---------- ✅ محتوای سلول را جدا می‌سازیم ----------
    cell_children = [
        ft.Text(str(i), size=13, weight=ft.FontWeight.BOLD, color=fg),
    ]

    if result == "success":
        cell_children.append(
            ft.Icon(ft.Icons.CHECK, size=10, color=fg)
        )
    elif result == "failure":
        cell_children.append(
            ft.Icon(ft.Icons.CLOSE, size=10, color=fg)
        )
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
        height=48,
        bgcolor=bg,
        border=border,
        border_radius=10,
        alignment=ft.Alignment.CENTER,
        ink=is_clickable,
        on_click=on_click if is_clickable else None,
        col={"xs": 3, "sm": 2, "md": 1.5},
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

# ---------- تاریخچه (بخش جدا) ----------
def _build_history_section(c) -> ft.Control | None:
    if not c.history:
        return None

    rows = []
    for h in reversed(c.history):
        is_success = h["status"] == "completed"
        status_text = "موفق" if is_success else "شکست"
        status_color = "#2E7D32" if is_success else "#C62828"

        rows.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.CHECK if is_success
                            else ft.Icons.CLOSE,
                            size=18, color=ft.Colors.WHITE,
                        ),
                        width=36, height=36,
                        bgcolor=status_color,
                        border_radius=18,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column([
                        ft.Row([
                            ft.Text(f"دوره {h['cycle']}", size=12,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text(status_text, size=9,
                                                color=ft.Colors.WHITE,
                                                weight=ft.FontWeight.BOLD),
                                padding=ft.Padding.symmetric(
                                    vertical=2, horizontal=8),
                                bgcolor=status_color,
                                border_radius=6,
                            ),
                        ], spacing=8),
                        ft.Text(
                            f"{to_jalali(date.fromisoformat(h['start_date']))} ← "
                            f"{to_jalali(date.fromisoformat(h['end_date']))}",
                            size=10, color=ft.Colors.GREY_600),
                    ], spacing=2, expand=True),
                    ft.Text(f"{h['days_completed']} روز",
                            size=11, weight=ft.FontWeight.BOLD,
                            color=status_color),
                ], spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border_radius=12,
            )
        )

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=18, color=ft.Colors.PRIMARY),
                ft.Text("تاریخچه دوره‌ها", size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(f"{len(c.history)} دوره", size=10,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                    padding=ft.Padding.symmetric(vertical=3, horizontal=10),
                    bgcolor=ft.Colors.PRIMARY,
                    border_radius=8,
                ),
            ], spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Column(rows, spacing=8),
        ], spacing=4),
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )