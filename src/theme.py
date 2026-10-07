import flet as ft


# ---------- پالت رنگ ----------
PRIMARY = "#0D47A1"          # آبی نیلی
PRIMARY_LIGHT = "#1976D2"
ACCENT = "#FFB300"           # طلایی
SUCCESS = "#2E7D32"
DANGER = "#C62828"
SURFACE = "#F5F7FA"
SURFACE_DARK = "#121212"
CARD_BG = "#FFFFFF"
CARD_BG_DARK = "#1E1E1E"


def make_appbar(
    title: str,
    subtitle: str = "",
    show_back: bool = False,
    on_back=None,
    actions: list | None = None,
) -> ft.AppBar:
    """ساخت AppBar یکپارچه برای همه صفحات"""
    leading = None
    if show_back:
        leading = ft.IconButton(
            ft.Icons.ARROW_FORWARD,   # در RTL به معنای بازگشت
            icon_color=ft.Colors.PRIMARY,
            tooltip="بازگشت",
            on_click=on_back,
        )

    title_control = ft.Column([
        ft.Text(title, size=16, weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY),
        *( [ft.Text(subtitle, size=11, color=ft.Colors.GREY_600,
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)]
           if subtitle else [] ),
    ], spacing=0, alignment=ft.MainAxisAlignment.CENTER)

    return ft.AppBar(
        leading=leading,
        leading_width=48 if show_back else 0,
        title=title_control,
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        elevation=0,
        actions=actions or [],
    )


# ---------- تم اصلی ----------
def app_theme() -> ft.Theme:
    return ft.Theme(
        font_family="Vazirmatn",
        color_scheme_seed=PRIMARY,
        color_scheme=ft.ColorScheme(
            primary=PRIMARY,
            secondary=ACCENT,
            surface=SURFACE,
            error=DANGER,
        ),
        visual_density=ft.VisualDensity.COMFORTABLE,
    )


def app_dark_theme() -> ft.Theme:
    return ft.Theme(
        font_family="Vazirmatn",
        color_scheme_seed=PRIMARY_LIGHT,
        color_scheme=ft.ColorScheme(
            primary=PRIMARY_LIGHT,
            secondary=ACCENT,
            surface=SURFACE_DARK,
            error=DANGER,
        ),
    )


# ---------- سبک‌های مشترک ----------
def elevated_card(content: ft.Control, padding: int = 14,
                  radius: int = 16) -> ft.Container:
    """کارت با گوشه گرد و سایه ملایم"""
    return ft.Container(
        content=content,
        padding=padding,
        border_radius=radius,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=12,
            spread_radius=0,
            color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
            offset=ft.Offset(0, 4),
        ),
    )

# header 
def gradient_header(title: str, subtitle: str = "",
                    icon=None) -> ft.Container:
    """هدر گرادیانی برای صفحات"""
    row_children = []
    if icon:
        row_children.append(ft.Icon(icon, color=ft.Colors.WHITE, size=28))
    row_children.append(
        ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            *( [ft.Text(subtitle, size=12,
                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE))]
               if subtitle else [] ),
        ], spacing=2, expand=True)
    )

    return ft.Container(
        content=ft.Row(row_children, spacing=12,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=18, horizontal=20),
        border_radius=ft.BorderRadius.only(
            bottom_left=20, bottom_right=20),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_RIGHT,
            end=ft.Alignment.BOTTOM_LEFT,
            colors=[PRIMARY, PRIMARY_LIGHT],
        ),
    )


def empty_state(icon, title: str, subtitle: str = "",
                action=None) -> ft.Container:
    """حالت خالی زیبا"""
    controls = [
        ft.Container(
            content=ft.Icon(icon, size=64,
                            color=ft.Colors.with_opacity(0.35, PRIMARY)),
            padding=20,
        ),
        ft.Text(title, size=17, weight=ft.FontWeight.BOLD,
                color=ft.Colors.GREY_700),
    ]
    if subtitle:
        controls.append(
            ft.Text(subtitle, size=13, color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER)
        )
    if action:
        controls.append(ft.Container(content=action, margin=ft.Margin.only(top=12)))

    return ft.Container(
        content=ft.Column(controls, spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.Alignment.CENTER,
        padding=40,
    )