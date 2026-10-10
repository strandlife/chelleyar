from datetime import date

import flet as ft


# ==================================================================
# محاسبه سطح اجرای چله
# ==================================================================

def _today_log(c):
    """لاگ امروز را از daily_logs برمی‌گرداند (یا None)."""
    logs = getattr(c, "daily_logs", None)
    if not isinstance(logs, dict):
        return None
    return logs.get(date.today().isoformat())


def _extract_score(log):
    """امتیاز عددی امروز را از ساختار لاگ استخراج می‌کند.

    ساختارهای پشتیبانی‌شده:
      • عدد خام (int / float)
      • دیکشنری با کلید «score»
      • دیکشنری با کلید «levels» شامل لیست امتیازها
    ⚠️ اگر ساختار daily_logs شما چیز دیگری است،
       فقط همین یک تابع را تغییر دهید.
    """
    if isinstance(log, (int, float)):
        return int(log)
    if isinstance(log, dict):
        if isinstance(log.get("score"), (int, float)):
            return int(log["score"])
        if isinstance(log.get("levels"), list):
            return sum(
                int(x) for x in log["levels"]
                if isinstance(x, (int, float))
            )
    return None


def get_current_level(c) -> dict | None:
    """سطح اجرای «امروز» چله را برمی‌گرداند.

    یعنی بالاترین سطحی که امتیاز ثبت‌شده امروز شرطش را برآورده کرده.
    اگر امروز لاگی ثبت نشده باشد، None برمی‌گرداند.
    """
    if not getattr(c, "levels", None):
        return None
    log = _today_log(c)
    if log is None:
        return None
    score = _extract_score(log)
    if score is None:
        return None

    current = None
    for lv in sorted(c.levels, key=lambda x: x.get("score", 0)):
        if score >= lv.get("score", 0):
            current = lv
    return current


# ==================================================================
# چیپ وضعیت
# ==================================================================

def _make_chip(text: str, color: str, icon=None) -> ft.Container:
    children = []
    if icon:
        children.append(ft.Icon(icon, size=12, color=color))
    else:
        children.append(ft.Container(
            width=8, height=8, bgcolor=color, border_radius=4))
    children.append(ft.Text(
        text, size=10, weight=ft.FontWeight.W_600, color=color,
        max_lines=1, overflow=ft.TextOverflow.ELLIPSIS))
    return ft.Container(
        content=ft.Row(children, spacing=4, tight=True),
        padding=ft.Padding.symmetric(vertical=4, horizontal=8),
        bgcolor=ft.Colors.with_opacity(0.12, color),
        border_radius=20,
    )


# ==================================================================
# کارت چله
# ==================================================================

def build_cheleh_card(app, c) -> ft.Control:
    day = c.current_day
    prog = c.progress()
    is_done = c.status == "completed"
    ratio = prog / c.total_days if c.total_days else 0

    # ---------- دایره روز ----------
    if is_done:
        circle_content = ft.Icon(ft.Icons.CHECK, color=ft.Colors.WHITE, size=22)
        circle_bg = "#2E7D32"
        bar_color = "#2E7D32"
    else:
        circle_content = ft.Text(str(day), size=16,
                                 weight=ft.FontWeight.BOLD,
                                 color=ft.Colors.WHITE)
        circle_bg = ft.Colors.PRIMARY
        bar_color = ft.Colors.PRIMARY

    # ---------- عنوان + برچسب تکمیل ----------
    title_row_children = [
        ft.Text(c.display_name, size=15,
                weight=ft.FontWeight.BOLD,
                max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                expand=True),
    ]
    if is_done:
        title_row_children.append(
            ft.Container(
                content=ft.Text("تکمیل", size=9,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD),
                padding=ft.Padding.symmetric(vertical=3, horizontal=8),
                bgcolor="#2E7D32",
                border_radius=8,
            )
        )

    title_row = ft.Row(
        title_row_children,
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- ردیف سطح اجرا (جدید) ----------
    lv = get_current_level(c)
    if is_done:
        chip = _make_chip("چله تکمیل شد", "#2E7D32", icon=ft.Icons.VERIFIED)
    elif lv:
        chip = _make_chip(lv["title"] or "بدون عنوان", lv["color"])
    else:
        chip = _make_chip("امروز ثبت نشده", ft.Colors.GREY_500)

    status_children = []
    if lv and not is_done:
        status_children.append(
            ft.Text("سطح امروز:", size=10, color=ft.Colors.GREY_500))
    status_children += [chip, ft.Container(expand=True)]
    status_children.append(
        ft.Text(f"روز {day} از {c.total_days}",
                size=10, color=ft.Colors.GREY_500))

    status_row = ft.Row(
        status_children, spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- منوی سه‌نقطه ----------
    def open_menu(e):
        page = app.page

        def go_edit(ev):
            page.pop_dialog()
            app.open_edit(c)

        def go_stats(ev):
            page.pop_dialog()
            app.open_stats(c)

        def go_delete(ev):
            page.pop_dialog()
            _show_delete_dialog(app, c)

        dialog = ft.AlertDialog(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EDIT_OUTLINED,
                                    color=ft.Colors.PRIMARY),
                    title=ft.Text("ویرایش چله"),
                    on_click=go_edit,
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INSIGHTS_OUTLINED,
                                    color=ft.Colors.ORANGE),
                    title=ft.Text("آمار و گزارش"),
                    on_click=go_stats,
                ),
                ft.Divider(height=1),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DELETE_OUTLINE,
                                    color=ft.Colors.RED_400),
                    title=ft.Text("حذف چله", color=ft.Colors.RED_400),
                    on_click=go_delete,
                ),
            ], spacing=0, tight=True, width=260),
            content_padding=ft.Padding.symmetric(vertical=8, horizontal=0),
        )
        page.show_dialog(dialog)

    # ---------- کارت اصلی ----------
    card = ft.Container(
        content=ft.Row([
            ft.Container(
                content=circle_content,
                width=52, height=52,
                bgcolor=circle_bg,
                border_radius=26,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column([
                title_row,
                ft.Text(c.task, size=11, color=ft.Colors.GREY_600,
                        max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                ft.Container(height=6),
                ft.Row([
                    ft.ProgressBar(
                        value=ratio,
                        color=bar_color,
                        bgcolor=ft.Colors.with_opacity(0.12, bar_color),
                        height=5, border_radius=3, expand=True,
                    ),
                    ft.Text(f"{int(ratio * 100)}٪", size=10,
                            color=bar_color, weight=ft.FontWeight.BOLD),
                ], spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Container(height=4),
                status_row,   # ➕ ردیف سطح اجرا
            ], spacing=3, expand=True),
            ft.IconButton(
                ft.Icons.MORE_VERT,
                icon_size=20,
                icon_color=ft.Colors.GREY_500,
                tooltip="گزینه‌ها",
                on_click=open_menu,
            ),
        ], spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=12, horizontal=12),
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
        ink=True,
        on_click=lambda e, ch=c: app.open_status(ch),
    )

    return card


# ==================================================================
# دیالوگ حذف (از list_view به اینجا منتقل شد)
# ==================================================================

def _show_delete_dialog(app, ch):
    page = app.page

    async def perform_delete():
        app.chelehs = [x for x in app.chelehs if x.id != ch.id]
        app.db.delete_cheleh(ch.id)
        app.snack("چله حذف شد")
        app.refresh()

    def on_dismiss(e):
        if getattr(dialog, "_confirmed", False):
            page.run_task(perform_delete)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.RED, size=26),
            ft.Text("حذف چله", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Text(
            f"آیا از حذف «{ch.display_name}» مطمئن هستید؟\n"
            "تمام تاریخچه و یادداشت‌ها پاک می‌شوند.",
            size=13,
        ),
        actions=[
            ft.TextButton(
                "انصراف",
                on_click=lambda e: (setattr(dialog, "_confirmed", False),
                                    page.pop_dialog()),
            ),
            ft.Button(
                "حذف",
                icon=ft.Icons.DELETE,
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