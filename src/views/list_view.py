import flet as ft
from chelleh_card import build_chelleh_card




def build_list_view(app) -> ft.Control:
    items = [build_chelleh_card(app, c) for c in app.chellehs]
    def open_edu():
        app.navigate('/science')

    if not items:
        top_space = max(40, int((app.page.height or 600) * 0.28))
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=top_space),
                    ft.Icon(
                        ft.Icons.AUTO_AWESOME,
                        size=56,
                        color=ft.Colors.with_opacity(0.35, ft.Colors.PRIMARY),
                    ),
                    ft.Container(height=8),
                    ft.Button('چله چیه؟!', on_click=open_edu),
                    ft.Text(
                        "هنوز چله‌ای نساخته‌اید",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                    ),
                    ft.Text(
                        "برای شروع یک سفر ۴۰ روزه، روی دکمه + بزنید",
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=40,
        )

    return ft.Column(items, spacing=0)