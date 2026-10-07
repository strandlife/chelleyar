import flet as ft


def build_list_view(app) -> ft.Control:
    items = [_build_cheleh_card(app, c) for c in app.chelehs]

    if not items:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.AUTO_AWESOME, size=56,
                        color=ft.Colors.with_opacity(0.35, ft.Colors.PRIMARY)),
                ft.Container(height=8),
                ft.Text("هنوز چله‌ای نساخته‌اید", size=16,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_700),
                ft.Text("برای شروع یک سفر ۴۰ روزه، روی دکمه + بزنید",
                        size=12, color=ft.Colors.GREY_500,
                        text_align=ft.TextAlign.CENTER),
            ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment.CENTER,
            padding=40, expand=True,
        )

    return ft.Column(items, spacing=10)


def _build_cheleh_card(app, c) -> ft.Control:
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

    # ---------- عنوان + برچسب تکمیل (لیست کنترل‌ها را جدا می‌سازیم) ----------
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