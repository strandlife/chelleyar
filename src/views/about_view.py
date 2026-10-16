import flet as ft

from theme import gradient_header, elevated_card


# ---------- اطلاعات طراح را اینجا پر کنید ----------
DESIGNER = {
    "name": "سید نصیب",
    "role": "دبیر علوم تجربی از کهگیلویه و بویر احمد",
    "bio": "عاشق ساختن ابزارهای ساده برای بهبود عادت‌ها و پیگیری مسیر رشد.",
    "email": "strandlife@chmail.ir",
    "github": "https://github.com/strandlife/chelleyar",
    "app_version": "0.1.0",
    "app_name": "چله‌یار",
    "app_description": (
        "«چله‌یار» ابزاری برای پیگیری چله‌های ۴۰ روزه است. "
        "کاربر می‌تواند برای هر روز یادداشت شروع و پایان ثبت کند، "
        "سطح وظیفه را انتخاب کند و پیشرفت خود را در نمودار ببیند."
    ),

    # ---------- لینک‌های حمایت ----------
    # لینک ثبت ایشوی جدید در گیت‌هاب
    "issues_url": "https://github.com/strandlife/chelleyar/issues/new",
    # لینک حمایت مالی — آن را با لینک واقعی خود جایگزین کنید
    # نمونه‌ها: زرین‌پال، حامی‌کارت، IDPay، Buy Me a Coffee
    "donate_url": "https://zarinp.al/username",
}



def _launch_url(app, url: str):
    """راه‌اندازی URL با سرویس UrlLauncher در Flet 1.0"""
    page = app.page
    launcher = None
    for s in getattr(page, "services", []):
        if isinstance(s, ft.UrlLauncher):
            launcher = s
            break
    if launcher is None:
        launcher = ft.UrlLauncher()
        page.services.append(launcher)

    page.run_task(launcher.launch_url, url)

def build_about_view(app) -> ft.Control:
    d = DESIGNER

    profile_card = _build_profile_card(d)
    contact_card = _build_contact_card(app, d)
    about_card = _build_about_app_card(d)
    support_card = _build_support_card(app, d)

    footer = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FAVORITE, size=12,
                        color=ft.Colors.RED_400),
                ft.Text("به امید پاک شدن ما از گناهان", size=11,
                        color=ft.Colors.GREY_600),
            ], spacing=4,
                alignment=ft.MainAxisAlignment.CENTER),
            ft.Text("Python + Flet", size=10,
                    color=ft.Colors.GREY_500),
        ], spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.only(top=10, bottom=20),
    )

    # روی دسکتاپ: پروفایل + ارتباطی کنار هم
    # روی موبایل: زیر هم
    top_row = ft.ResponsiveRow([
        ft.Column([profile_card], col={"xs": 12, "md": 6}),
        ft.Column([contact_card], col={"xs": 12, "md": 6}),
    ], spacing=14, run_spacing=14)

    return ft.Column([
        ft.Container(
            content=ft.Column([
                top_row,
                ft.Container(height=14),
                about_card,
                ft.Container(height=14),
                support_card,
                footer,
            ], spacing=0),
            padding=ft.Padding.symmetric(vertical=16, horizontal=16),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)

# ---------- کارت پروفایل طراح ----------
def _build_profile_card(d: dict) -> ft.Container:
    avatar = ft.Container(
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
    )

    info = ft.Column([
        ft.Text(d["name"], size=20, weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE),
        ft.Container(
            content=ft.Text(d["role"], size=12,
                            color=ft.Colors.WHITE),
            padding=ft.Padding.symmetric(vertical=4, horizontal=12),
            bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
            border_radius=12,
        ),
        ft.Container(height=6),
        ft.Text(d["bio"], size=12,
                color=ft.Colors.with_opacity(0.9, ft.Colors.WHITE),
                text_align=ft.TextAlign.CENTER),
    ], spacing=6,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # چیدمان داخلی: روی دسکتاپ آواتار کنار اطلاعات، روی موبایل زیر هم
    inner = ft.ResponsiveRow([
        ft.Column([avatar], col={"xs": 12, "md": 3},
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Column([info], col={"xs": 12, "md": 9},
                  horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    ], spacing=12, run_spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER)

    return ft.Container(
        content=inner,
        padding=ft.Padding.symmetric(vertical=24, horizontal=20),
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
        on_click=lambda e: _launch_url(app, f"mailto:{d['email']}"),
    )
    github_row = _contact_item(
        icon=ft.Icons.CODE,
        title="گیت‌هاب",
        value=d["github"].replace("https://", ""),
        color="#212121",
        on_click=lambda e: _launch_url(app, d["github"]),
    )

    # روی موبایل: زیر هم (پیش‌فرض)
    # روی دسکتاپ: کنار هم
    items = ft.ResponsiveRow([
        ft.Column([email_row], col={"xs": 12, "md": 6}),
        ft.Column([github_row], col={"xs": 12, "md": 6}),
    ], spacing=10, run_spacing=10)

    return elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CONNECT_WITHOUT_CONTACT, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("راه‌های ارتباطی", size=14,
                        weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=6),
            items,
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

            ft.Text(d["app_description"], size=12,
                    color=ft.Colors.GREY_700),

            ft.Container(height=8),

            _feature_row(ft.Icons.CALENDAR_MONTH,
                         "پیگیری ۴۰ روزه یک هدف مشخص با کمک تاریخ شمسی"),
            _feature_row(ft.Icons.LAYERS,
                         "تعیین سطوح وظیفه به همراه امتیاز بندی و رنگ اختصاصی"),
            _feature_row(ft.Icons.HISTORY,
                         "ذخیره تاریخچه دوره‌های موفق و ناموفق"),
            _feature_row(ft.Icons.INSIGHTS,
                         "مشاهده نمودار و آمار پیشرفت روزانه"),
            _feature_row(ft.Icons.EDIT_NOTE,
                         "نوشتن یادداشت جداگانه برای شروع و پایان یک روز"),
        ], spacing=6),
        padding=16,
    )


def _feature_row(icon, text: str) -> ft.Row:
    return ft.Row([
        ft.Icon(icon, size=14, color=ft.Colors.PRIMARY),
        ft.Text(text, size=11, color=ft.Colors.GREY_700, expand=True),
    ], spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER)


def _support_button(icon, title: str, subtitle: str,
                    colors: list, shadow_color: str,
                    on_click, badge: str | None) -> ft.Container:
    """دکمه حمایت با گرادیان و محتوای مشترک"""
    row_children = [
        ft.Container(
            content=ft.Icon(icon, color=ft.Colors.WHITE, size=22),
            width=44, height=44,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            border_radius=12,
            alignment=ft.Alignment.CENTER,
        ),
        ft.Column([
            ft.Text(title, size=13,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
            ft.Text(subtitle, size=10,
                    color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
        ], spacing=2, expand=True),
    ]

    if badge:
        row_children.append(
            ft.Container(
                content=ft.Text(badge, size=9,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD),
                padding=ft.Padding.symmetric(vertical=3, horizontal=8),
                bgcolor=ft.Colors.with_opacity(0.25, ft.Colors.WHITE),
                border_radius=8,
            )
        )
    else:
        row_children.append(
            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=14,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE))
        )

    return ft.Container(
        content=ft.Row(row_children, spacing=12,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=14, horizontal=14),
        border_radius=14,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_RIGHT,
            end=ft.Alignment.BOTTOM_LEFT,
            colors=colors,
        ),
        shadow=ft.BoxShadow(
            blur_radius=10, spread_radius=0,
            color=ft.Colors.with_opacity(0.15, shadow_color),
            offset=ft.Offset(0, 4),
        ),
        ink=True,
        on_click=on_click,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

# ==================================================================
# کارت حمایت و درخواست ویژگی
# ==================================================================

def _build_support_card(app, d: dict) -> ft.Container:
    page = app.page

    # ---------- دکمه ۱: درخواست ویژگی ----------
    def open_feature_request(e):
        _launch_url(app, d["issues_url"])

    feature_btn = _support_button(
        icon=ft.Icons.LIGHTBULB_OUTLINE,
        title="درخواست ویژگی",
        subtitle="ایده یا پیشنهاد خود را ثبت کنید",
        colors=["#1976D2", "#42A5F5"],
        shadow_color="#1976D2",
        on_click=open_feature_request,
        badge=None,
    )

    # ---------- دکمه ۲: حمایت + درخواست ویژگی ----------
    def open_combo(e):
        _show_combo_dialog(app, d)

    combo_btn = _support_button(
        icon=ft.Icons.FAVORITE,
        title="حمایت + درخواست ویژگی",
        subtitle="پیشنهاد خود را همراه با حمایت ارسال کنید",
        colors=["#7B1FA2", "#E91E63"],
        shadow_color="#7B1FA2",
        on_click=open_combo,
        badge="ویژه",
    )

    # ---------- دکمه ۳: کمک مالی ----------
    def open_donate(e):
        _launch_url(app, d["donate_url"])

    donate_btn = _support_button(
        icon=ft.Icons.COFFEE,
        title="کمک مالی",
        subtitle="از توسعه برنامه حمایت کنید",
        colors=["#00897B", "#26A69A"],
        shadow_color="#00897B",
        on_click=open_donate,
        badge=None,
    )

    # ---------- چیدمان دکمه‌ها ----------
    buttons = ft.ResponsiveRow([
        ft.Column([feature_btn], col={"xs": 12, "md": 4}),
        ft.Column([combo_btn], col={"xs": 12, "md": 4}),
        ft.Column([donate_btn], col={"xs": 12, "md": 4}),
    ], spacing=10, run_spacing=10)

    return elevated_card(
        ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.VOLUNTEER_ACTIVISM,
                                    size=20, color=ft.Colors.WHITE),
                    width=40, height=40,
                    bgcolor=ft.Colors.PRIMARY,
                    border_radius=10,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column([
                    ft.Text("حمایت از چله‌یار", size=14,
                            weight=ft.FontWeight.BOLD),
                    ft.Text("با پیشنهاد و حمایت، به بهبود کمک کنید",
                            size=10, color=ft.Colors.GREY_600),
                ], spacing=0, expand=True),
            ], spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER),

            ft.Container(height=12),
            buttons,
        ], spacing=4),
        padding=16,
    )


# ---------- دیالوگ پیشنهاد ویژه ----------
def _show_combo_dialog(app, d: dict):
    page = app.page

    def open_issues(e):
        page.pop_dialog()
        _launch_url(app, d["issues_url"])

    def open_donate(e):
        page.pop_dialog()
        _launch_url(app, d["donate_url"])

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.FAVORITE, color="#E91E63", size=26),
            ft.Text("حمایت + پیشنهاد", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Column([
            ft.Text(
                "ممنون که می‌خواهید هم پیشنهاد بدهید و هم از برنامه "
                "حمایت کنید. لطفاً مراحل زیر را انجام دهید:",
                size=13,
            ),
            ft.Container(height=8),
            _step_row("۱", "ابتدا پیشنهاد یا ایده خود را ثبت کنید"),
            ft.Container(height=6),
            _step_row("۲", "سپس از طریق لینک حمایت، مبلغ دلخواه را "
                           "اهداء کنید"),
            ft.Container(height=8),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, size=14,
                            color=ft.Colors.BLUE_700),
                    ft.Text(
                        "پیشنهادهای همراه با حمایت، در اولویت بررسی قرار می‌گیرند.",
                        size=11, color=ft.Colors.BLUE_700),
                ], spacing=6),
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.BLUE),
                border_radius=8,
            ),
        ], spacing=4, tight=True, width=340),
        actions=[
            ft.TextButton("انصراف", on_click=lambda e: page.pop_dialog()),
            ft.TextButton(
                "فقط حمایت",
                icon=ft.Icons.COFFEE,
                on_click=open_donate,
            ),
            ft.Button(
                "ثبت پیشنهاد",
                icon=ft.Icons.LIGHTBULB_OUTLINE,
                on_click=open_issues,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                ),
            ),
        ],
    )
    page.show_dialog(dialog)


def _step_row(number: str, text: str) -> ft.Row:
    return ft.Row([
        ft.Container(
            content=ft.Text(number, size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.BOLD),
            width=26, height=26,
            bgcolor=ft.Colors.PRIMARY,
            border_radius=13,
            alignment=ft.Alignment.CENTER,
        ),
        ft.Text(text, size=12, expand=True),
    ], spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER)