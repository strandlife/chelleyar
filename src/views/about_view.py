import flet as ft

from theme import gradient_header, elevated_card


# ---------- اطلاعات طراح را اینجا پر کنید ----------
DESIGNER = {
    "name": "سید نصیب",
    "role": "توسعه‌دهنده Python و Flet",
    "bio": "عاشق ساختن ابزارهای ساده برای بهبود عادت‌ها و پیگیری مسیر معنوی.",
    "email": "you@example.com",
    "github": "https://github.com/username",
    "app_version": "1.0.0",
    "app_name": "چله‌یار",
    "app_description": (
        "«چله‌یار» ابزاری برای پیگیری چله‌های ۴۰ روزه است. "
        "کاربر می‌تواند برای هر روز یادداشت شروع و پایان ثبت کند، "
        "سطح وظیفه را انتخاب کند و پیشرفت خود را در نمودار ببیند."
    ),
}


def build_about_view(app) -> ft.Control:
    d = DESIGNER

    # ---------- کارت پروفایل طراح ----------
    profile_card = _build_profile_card(d)

    # ---------- بخش راه‌های ارتباطی ----------
    contact_card = _build_contact_card(app, d)

    # ---------- بخش درباره برنامه ----------
    about_card = _build_about_app_card(d)

    # ---------- فوتر ----------
    footer = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FAVORITE, size=12,
                        color=ft.Colors.RED_400),
                ft.Text("ساخته‌شده با عشق", size=11,
                        color=ft.Colors.GREY_600),
            ], spacing=4,
                alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("Python + Flet", size=10,
                    color=ft.Colors.GREY_500),
        ], spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.only(top=10, bottom=20),
    )

    # ---------- UI نهایی ----------
    return ft.Column([
        ft.Container(
            content=ft.Column([
                profile_card,
                ft.Container(height=14),
                contact_card,
                ft.Container(height=14),
                about_card,
                footer,
            ], spacing=0),
            padding=ft.Padding.symmetric(vertical=16, horizontal=16),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)


# ---------- کارت پروفایل طراح ----------
def _build_profile_card(d: dict) -> ft.Container:
    return ft.Container(
        content=ft.Column([
            # آواتار با حلقه رنگی
            ft.Container(
                content=ft.Container(
                    content=ft.Icon(ft.Icons.PERSON, size=48,
                                    color=ft.Colors.WHITE),
                    width=96, height=96,
                    bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                    border_radius=48,
                    alignment=ft.Alignment.CENTER,
                ),
                padding=4,
                border=ft.Border.all(
                    2, ft.Colors.with_opacity(0.4, ft.Colors.WHITE)),
                border_radius=54,
            ),
            ft.Container(height=12),
            ft.Text(d["name"], size=20, weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE),
            ft.Container(
                content=ft.Text(d["role"], size=12,
                                color=ft.Colors.WHITE),
                padding=ft.Padding.symmetric(vertical=4, horizontal=12),
                bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
                border_radius=12,
            ),
            ft.Container(height=10),
            ft.Text(d["bio"], size=12,
                    color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                    text_align=ft.TextAlign.CENTER),
        ], spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=28, horizontal=20),
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_RIGHT,
            end=ft.Alignment.BOTTOM_LEFT,
            colors=["#0D47A1", "#1976D2", "#42A5F5"],
        ),
        shadow=ft.BoxShadow(
            blur_radius=14, spread_radius=0,
            color=ft.Colors.with_opacity(0.2, "#0D47A1"),
            offset=ft.Offset(0, 6),
        ),
    )


# ---------- کارت راه‌های ارتباطی ----------
def _build_contact_card(app, d: dict) -> ft.Container:
    email_row = _contact_item(
        icon=ft.Icons.EMAIL_OUTLINED,
        title="ایمیل",
        value=d["email"],
        color="#1976D2",
        on_click=lambda e: app.page.launch_url(f"mailto:{d['email']}"),
    )
    github_row = _contact_item(
        icon=ft.Icons.CODE,
        title="گیت‌هاب",
        value=d["github"].replace("https://", ""),
        color="#212121",
        on_click=lambda e: app.page.launch_url(d["github"]),
    )

    return elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CONNECT_WITHOUT_CONTACT, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("راه‌های ارتباطی", size=14,
                        weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=6),
            email_row,
            ft.Divider(height=1, color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
            github_row,
        ], spacing=4),
        padding=16,
    )


def _contact_item(icon, title: str, value: str, color,
                  on_click) -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(icon, size=18, color=color),
                width=40, height=40,
                bgcolor=ft.Colors.with_opacity(0.12, color),
                border_radius=10,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column([
                ft.Text(title, size=10, color=ft.Colors.GREY_600),
                ft.Text(value, size=12, weight=ft.FontWeight.W_500),
            ], spacing=0, expand=True),
            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=12,
                    color=ft.Colors.GREY_400),
        ], spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=8, horizontal=6),
        border_radius=10,
        ink=True,
        on_click=on_click,
    )


# ---------- کارت درباره برنامه ----------
def _build_about_app_card(d: dict) -> ft.Container:
    return elevated_card(
        ft.Column([
            # هدر
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.AUTO_AWESOME,
                                    size=20, color=ft.Colors.WHITE),
                    width=40, height=40,
                    bgcolor=ft.Colors.PRIMARY,
                    border_radius=10,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text(d["app_name"], size=15,
                            weight=ft.FontWeight.BOLD),
                    ft.Text(f"نسخه {d['app_version']}", size=10,
                            color=ft.Colors.GREY_600),
                ], spacing=0),
            ], spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),

            ft.Container(height=4),
            ft.Divider(height=1,
                       color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK)),
            ft.Container(height=4),

            # توضیحات
            ft.Text(d["app_description"], size=12,
                    color=ft.Colors.GREY_700),

            ft.Container(height=8),

            # ویژگی‌های برنامه
            _feature_row(ft.Icons.CALENDAR_MONTH,
                         "پیگیری ۴۰ روزه با تاریخ شمسی"),
            _feature_row(ft.Icons.LAYERS,
                         "سطوح وظیفه با امتیاز و رنگ اختصاصی"),
            _feature_row(ft.Icons.HISTORY,
                         "ذخیره تاریخچه دوره‌های موفق و ناموفق"),
            _feature_row(ft.Icons.INSIGHTS,
                         "نمودار و آمار پیشرفت روزانه"),
            _feature_row(ft.Icons.EDIT_NOTE,
                         "یادداشت جداگانه برای شروع و پایان روز"),
        ], spacing=6),
        padding=16,
    )


def _feature_row(icon, text: str) -> ft.Row:
    return ft.Row([
        ft.Icon(icon, size=14, color=ft.Colors.PRIMARY),
        ft.Text(text, size=11, color=ft.Colors.GREY_700, expand=True),
    ], spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER)