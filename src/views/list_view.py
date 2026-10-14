import flet as ft
from chelleh_card import build_chelleh_card




def build_list_view(app) -> ft.Control:
    items = [build_chelleh_card(app, c) for c in app.chellehs]

    if not items:
        return ft.Container(
            content=ft.Column([
                ft.Icon(
                    ft.Icons.AUTO_AWESOME,
                    size=56,
                    color=ft.Colors.with_opacity(0.35, ft.Colors.PRIMARY)),
                ft.Container(height=8),
                ft.Text(
                    "هنوز چله‌ای نساخته‌اید",
                    size=16,
                    weight=ft.
                    FontWeight.BOLD,
                    color=ft.Colors.GREY_700
                    ),
                ft.Text(
                    "برای شروع یک سفر ۴۰ روزه، روی دکمه + بزنید",
                    size=12,
                    color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER
                    ),
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            alignment=ft.Alignment.CENTER,
            padding=40,
            expand=True,
        )

    return ft.Column(items, spacing=10)