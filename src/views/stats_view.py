from datetime import date, timedelta
import flet as ft
import flet_charts as fch

from theme import gradient_header, elevated_card
from utils import to_jalali


def build_stats_view(app) -> ft.Control:
    page = app.page
    c = app.current_cheleh

    # ---------- بررسی وجود چله ----------
    if not c:
        return ft.SafeArea(
            content=ft.Column([
                ft.Text("چله‌ای انتخاب نشده"),
                ft.TextButton("بازگشت", on_click=lambda e: app.navigate("/")),
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
        )

    # ---------- محاسبه آمار ----------
    start = date.fromisoformat(c.cycle_start_date) if c.cycle_start_date else date.today()
    total_score = 0
    done_days = 0
    failed_days = 0
    best_day_score = 0
    best_day_num = 0
    success_level_counts = {}   # {level_index: count}

    for i in range(1, c.total_days + 1):
        rec = c.daily_logs.get(str(i), {})
        result = rec.get("result")

        if result == "success":
            score = rec.get("score", 0)
            total_score += score
            done_days += 1
            li = rec.get("level_index", 0)
            success_level_counts[li] = success_level_counts.get(li, 0) + 1
            if score > best_day_score:
                best_day_score = score
                best_day_num = i
        elif result == "failure":
            failed_days += 1

    avg = round(total_score / done_days, 1) if done_days else 0
    success_rate = round(done_days / c.total_days * 100) if c.total_days else 0

    # ---------- هدر ----------
    # header = gradient_header(
    #     title="آمار و گزارش",
    #     subtitle=c.display_name,
    #     icon=ft.Icons.INSIGHTS,
    # )

    # ---------- کارت‌های خلاصه ----------
    summary_row = ft.ResponsiveRow([
        _stat_card(
            icon=ft.Icons.CHECK_CIRCLE_OUTLINE,
            label="روزهای موفق",
            value=f"{done_days}",
            subtitle=f"از {c.total_days} روز",
            color="#2E7D32",
            col={"xs": 6, "sm": 6, "md": 3},
        ),
        _stat_card(
            icon=ft.Icons.STAR_OUTLINE,
            label="مجموع امتیاز",
            value=f"{total_score}",
            subtitle=f"میانگین {avg} در روز",
            color="#F57C00",
            col={"xs": 6, "sm": 6, "md": 3},
        ),
        _stat_card(
            icon=ft.Icons.TRENDING_UP,
            label="نرخ موفقیت",
            value=f"{success_rate}٪",
            subtitle=f"{failed_days} روز شکست",
            color="#1976D2",
            col={"xs": 6, "sm": 6, "md": 3},
        ),
        _stat_card(
            icon=ft.Icons.EMOJI_EVENTS,
            label="بهترین روز",
            value=f"روز {best_day_num}" if best_day_num else "—",
            subtitle=f"{best_day_score} امتیاز" if best_day_score else "ثبت نشده",
            color="#7B1FA2",
            col={"xs": 6, "sm": 6, "md": 3},
        ),
    ], spacing=10, run_spacing=10)

    # ---------- نمودار ستونی ----------
    chart_groups = []
    for i in range(c.total_days):
        day_key = str(i + 1)
        rec = c.daily_logs.get(day_key, {})
        result = rec.get("result")

        if result == "success":
            score = rec.get("score", 0)
            li = rec.get("level_index", 0)
            if 0 <= li < len(c.levels):
                rod_color = c.levels[li]["color"]
            else:
                rod_color = "#4CAF50"
        elif result == "failure":
            score = 0
            rod_color = "#C62828"
        else:
            score = 0
            rod_color = ft.Colors.with_opacity(0.15, ft.Colors.GREY)

        chart_groups.append(
            fch.BarChartGroup(
                x=i,
                rods=[
                    fch.BarChartRod(
                        from_y=0,
                        to_y=score if score > 0 else 0.1,
                        color=rod_color,
                        width=8,
                        border_radius=3,
                        tooltip=f"روز {i+1}: {score} امتیاز",
                    )
                ],
            )
        )

    max_score = max([lv["score"] for lv in c.levels] + [1])
    max_y = max_score + 1

    chart = fch.BarChart(
        groups=chart_groups,
        bottom_axis=fch.ChartAxis(
            labels=[
                fch.ChartAxisLabel(
                    value=j,
                    label=ft.Text(str(j + 1), size=8),
                )
                for j in range(0, c.total_days, max(1, c.total_days // 8))
            ],
            label_size=20,
        ),
        left_axis=fch.ChartAxis(
            label_size=24,
            title=ft.Text("امتیاز", size=10),
        ),
        horizontal_grid_lines=fch.ChartGridLines(
            interval=1,
            color=ft.Colors.with_opacity(0.1, ft.Colors.GREY),
            width=0.5,
        ),
        tooltip=fch.BarChartTooltip(
            bgcolor=ft.Colors.with_opacity(0.9, "#212121"),
            border_radius=8,
        ),
        max_y=max_y,
        interactive=True,
        expand=True,
    )

    chart_card = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.BAR_CHART, size=18, color=ft.Colors.PRIMARY),
                ft.Text("نمودار امتیاز روزانه", size=14,
                        weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(
                content=chart,
                height=240,
                padding=ft.Padding.only(top=12),
            ),
            # راهنمای رنگ
            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Container(width=12, height=12, bgcolor="#2E7D32",
                                     border_radius=3),
                        ft.Text("موفق", size=10, color=ft.Colors.GREY_600),
                    ], spacing=4),
                    ft.Row([
                        ft.Container(width=12, height=12, bgcolor="#C62828",
                                     border_radius=3),
                        ft.Text("شکست", size=10, color=ft.Colors.GREY_600),
                    ], spacing=4),
                    ft.Row([
                        ft.Container(
                            width=12, height=12,
                            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.GREY),
                            border_radius=3),
                        ft.Text("بدون ثبت", size=10, color=ft.Colors.GREY_600),
                    ], spacing=4),
                ], spacing=14, wrap=True, run_spacing=6),
                padding=ft.Padding.only(top=8),
            ),
        ], spacing=6),
        padding=16,
    )

    # ---------- تفکیک بر اساس سطوح ----------
    level_stats = []
    for i, lv in enumerate(c.levels):
        count = success_level_counts.get(i, 0)
        level_stats.append(
            _level_stat_row(lv, count, done_days)
        )

    levels_card = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LAYERS_OUTLINED, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("تفکیک سطوح", size=14,
                        weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=4),
            *level_stats,
        ], spacing=8),
        padding=16,
    )

    # ---------- جزئیات روزهای انجام‌شده ----------
    detail_rows = []
    for i in range(1, c.total_days + 1):
        rec = c.daily_logs.get(str(i), {})
        if rec.get("result") != "success":
            continue
        li = rec.get("level_index", 0)
        title = c.levels[li]["title"] if 0 <= li < len(c.levels) else "-"
        color = c.levels[li]["color"] if 0 <= li < len(c.levels) else "#4CAF50"

        # تاریخ تقریبی (روز i ام بعد از شروع دوره)
        d = start + timedelta(days=i - 1)

        detail_rows.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(str(i), size=11,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD),
                        width=32, height=32,
                        bgcolor=color,
                        border_radius=16,
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column([
                        ft.Text(title, size=12,
                                weight=ft.FontWeight.W_500),
                        ft.Text(to_jalali(d), size=10,
                                color=ft.Colors.GREY_600),
                    ], spacing=0, expand=True),
                    ft.Container(
                        content=ft.Text(f"{rec.get('score', 0)}+",
                                        size=12, color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD),
                        padding=ft.Padding.symmetric(
                            vertical=4, horizontal=10),
                        bgcolor=color,
                        border_radius=10,
                    ),
                ], spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=8,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border_radius=10,
            )
        )

    if detail_rows:
        details_content = ft.Column(detail_rows, spacing=6)
    else:
        details_content = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INBOX_OUTLINED, size=36,
                        color=ft.Colors.GREY_400),
                ft.Text("هنوز روزی ثبت نشده است", size=12,
                        color=ft.Colors.GREY_600),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6),
            alignment=ft.Alignment.CENTER,
            padding=30,
        )

    details_card = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.LIST_ALT_OUTLINED, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("جزئیات روزهای موفق", size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(f"{done_days} روز", size=10,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                    padding=ft.Padding.symmetric(vertical=4, horizontal=10),
                    bgcolor=ft.Colors.PRIMARY,
                    border_radius=10,
                ),
            ], spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=4),
            details_content,
        ], spacing=8),
        padding=16,
    )

    # ---------- تاریخچه دوره‌ها ----------
    history_card = _build_history_card(c)

    # ---------- بازگشت ----------
    back_row = ft.Row([
        ft.TextButton(
            "بازگشت",
            icon=ft.Icons.ARROW_FORWARD,
            on_click=lambda e: app.navigate("/status"),
            style=ft.ButtonStyle(color=ft.Colors.GREY_700),
        ),
    ])

    # ---------- ساختار نهایی ----------
    return ft.Column([
        # header,
        ft.Container(
            content=ft.Column([
                summary_row,
                chart_card,
                levels_card,
                details_card,
                history_card if history_card else ft.Container(),
                back_row,
                ft.Container(height=24),
            ], spacing=14),
            padding=ft.Padding.only(left=16, right=16, top=16, bottom=8),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)


# ---------- کارت آمار ----------
def _stat_card(icon, label: str, value: str, subtitle: str,
               color: str, col) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=18, color=color),
                    padding=8,
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=10,
                ),
                ft.Container(expand=True),
            ]),
            ft.Container(height=4),
            ft.Text(value, size=22, weight=ft.FontWeight.BOLD,
                    color=color),
            ft.Text(label, size=12, weight=ft.FontWeight.W_500),
            ft.Text(subtitle, size=10, color=ft.Colors.GREY_600),
        ], spacing=2),
        padding=14,
        border_radius=14,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        border=ft.Border.all(
            1, ft.Colors.with_opacity(0.08, color)),
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
        col=col,
    )


# ---------- ردیف تفکیک سطح ----------
def _level_stat_row(lv: dict, count: int, total: int) -> ft.Container:
    ratio = count / total if total else 0
    color = lv["color"]

    return ft.Container(
        content=ft.Row([
            ft.Container(
                width=14, height=14,
                bgcolor=color,
                border_radius=4,
            ),
            ft.Column([
                ft.Text(lv["title"], size=12,
                        weight=ft.FontWeight.W_500,
                        max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Text(f"{lv['score']} امتیاز", size=10,
                        color=ft.Colors.GREY_600),
            ], spacing=0, expand=True),
            ft.Column([
                ft.Text(f"{count}", size=14, weight=ft.FontWeight.BOLD,
                        color=color),
                ft.Text(f"{int(ratio * 100)}٪", size=9,
                        color=ft.Colors.GREY_600),
            ], spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.END),
        ], spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=6, horizontal=8),
    )


# ---------- کارت تاریخچه ----------
def _build_history_card(c) -> ft.Container | None:
    if not c.history:
        return None

    rows = []
    for h in reversed(c.history):
        is_success = h["status"] == "completed"
        status_text = "موفق ✅" if is_success else "شکست ❌"
        status_color = "#2E7D32" if is_success else "#C62828"

        rows.append(
            ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Icon(
                            ft.Icons.CHECK_CIRCLE if is_success
                            else ft.Icons.CANCEL,
                            size=20, color=status_color,
                        ),
                        padding=8,
                        bgcolor=ft.Colors.with_opacity(0.12, status_color),
                        border_radius=10,
                    ),
                    ft.Column([
                        ft.Row([
                            ft.Text(f"دوره {h['cycle']}", size=12,
                                    weight=ft.FontWeight.BOLD),
                            ft.Container(
                                content=ft.Text(status_text, size=10,
                                                color=ft.Colors.WHITE,
                                                weight=ft.FontWeight.BOLD),
                                padding=ft.Padding.symmetric(
                                    vertical=2, horizontal=8),
                                bgcolor=status_color,
                                border_radius=8,
                            ),
                        ], spacing=8),
                        ft.Text(
                            f"{to_jalali(date.fromisoformat(h['start_date']))} "
                            f"← {to_jalali(date.fromisoformat(h['end_date']))}",
                            size=10, color=ft.Colors.GREY_600,
                        ),
                        ft.Text(f"{h['days_completed']} روز موفق", size=10),
                    ], spacing=2, expand=True),
                ], spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10,
                bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
                border_radius=12,
            )
        )

    return elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.HISTORY, size=18, color=ft.Colors.PRIMARY),
                ft.Text("تاریخچه دوره‌ها", size=14,
                        weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Text(f"{len(c.history)} دوره", size=10,
                                    color=ft.Colors.WHITE,
                                    weight=ft.FontWeight.BOLD),
                    padding=ft.Padding.symmetric(vertical=4, horizontal=10),
                    bgcolor=ft.Colors.PRIMARY,
                    border_radius=10,
                ),
            ], spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=4),
            ft.Column(rows, spacing=8),
        ], spacing=8),
        padding=16,
    )