import flet as ft


# ==================================================================
# صفحه‌ی پشتوانه‌ی علمی — نوروپلاستیسیته و سازوکار عادت
# ==================================================================

ACCENT = "#5C6BC0"


def _card(content: ft.Control) -> ft.Container:
    """کارت استاندارد — هم‌سبک با کارت‌های چله."""
    return ft.Container(
        content=content,
        padding=ft.Padding.all(14),
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )


def _section(title: str, body: str, icon, color) -> ft.Control:
    """یک بخش: آیکون + عنوان + متن توضیحی."""
    return _card(
        ft.Row(
            [
                ft.Container(
                    content=ft.Icon(icon, color=color, size=22),
                    width=44, height=44,
                    bgcolor=ft.Colors.with_opacity(0.12, color),
                    border_radius=12,
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    [
                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(
                            body,
                            size=12, color=ft.Colors.GREY_700,
                            text_align=ft.TextAlign.START,
                        ),
                    ],
                    spacing=6,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
    )


def _hero() -> ft.Control:
    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.PSYCHOLOGY, size=28,
                                color=ft.Colors.WHITE),
                        ft.Text("چگونه ۴۰ روز، مغز را بازسازی می‌کند؟",
                                size=16, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE, expand=True),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "چله‌نشینی سنت کهنی برای ساختن تغییر است. امروز علوم اعصاب "
                    "می‌داند چرا کار می‌کند: تکرارِ منظم، مسیرهای عصبیِ رفتار جدید "
                    "را تقویت می‌کند تا رفتار از «تصمیمِ روزانه» به «خودکار بودن» "
                    "برسد. در ادامه، سازوکارهای اصلی را می‌بینید.",
                    size=12,
                    color=ft.Colors.with_opacity(0.92, ft.Colors.WHITE),
                ),
            ],
            spacing=8,
        ),
        padding=ft.Padding.all(16),
        border_radius=16,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_RIGHT,
            end=ft.Alignment.BOTTOM_LEFT,
            colors=["#5C6BC0", "#7E57C2"],
        ),
    )


def _stat_chip(value: str, label: str, color: str) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(value, size=14, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=9, color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER),
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        ),
        padding=ft.Padding.symmetric(vertical=8, horizontal=6),
        bgcolor=ft.Colors.with_opacity(0.08, color),
        border_radius=12,
        expand=True,
    )


def _forty_days_section() -> ft.Control:
    return _card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CALENDAR_TODAY, size=18, color="#7B1FA2"),
                        ft.Text("چرا ۴۰ روز؟ (و صادقانه بگوییم)",
                                size=13.5, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "پژوهش‌ها نشان می‌دهد خودکار شدن یک رفتار به‌طور میانگین حدود "
                    "۶۶ روز طول می‌کشد و بازه‌ی فردی آن بسیار متغیر است "
                    "(Lally و همکاران، ۲۰۱۰). پس «۲۱ روز کافی است» افسانه است. "
                    "عدد ۴۰ که از سنت چله‌نشینی به ما رسیده، یک آستانه‌ی تعهد "
                    "هوشمندانه است: آن‌قدر بلند که مدارهای عصبی فرصت تثبیت پیدا "
                    "کنند و آن‌قدر پایان‌پذیر که افق مسیر، انگیزه بماند.",
                    size=12, color=ft.Colors.GREY_700,
                    text_align=ft.TextAlign.START,
                ),
                ft.Row(
                    [
                        _stat_chip("۶۶ روز", "میانگین خودکار شدن\nرفتار جدید", "#7B1FA2"),
                        _stat_chip("۱۸ تا ۲۵۴", "بازه‌ی فردی در\nپژوهش‌ها", ACCENT),
                        _stat_chip("۴۰ روز", "آستانه‌ی تعهد\nدر چله", "#2E7D32"),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "نکته‌ی دلگرم‌کننده: در همین پژوهش، جا ماندنِ یک روز، روند "
                    "شکل‌گیری عادت را مختل نکرد. پس روز جامانده بهانه‌ی رها کردن "
                    "نیست — جبران کنید و ادامه دهید.",
                    size=11, color=ft.Colors.GREY_600,
                    text_align=ft.TextAlign.START,
                ),
            ],
            spacing=10,
        ),
    )


def _tool_row(icon, text: str) -> ft.Row:
    return ft.Row(
        [
            ft.Icon(icon, size=16, color=ACCENT),
            ft.Text(text, size=12, color=ft.Colors.GREY_700,
                    text_align=ft.TextAlign.START, expand=True),
        ],
        spacing=8,
    )


def _tools_section() -> ft.Control:
    return _card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.FACT_CHECK, size=18, color=ACCENT),
                        ft.Text("چله‌یار دقیقاً همین سازوکارها را هدف گرفته",
                                size=13.5, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                ),
                ft.Container(height=2),
                _tool_row(ft.Icons.LAYERS,
                          "سطح‌بندی روزانه: موفقیتِ پله‌ای حتی در روزهای سخت، "
                          "مدار پاداش را روشن نگه می‌دارد."),
                _tool_row(ft.Icons.SCHEDULE,
                          "ثبت صبح و شب: پیوند رفتار با نشانه‌های زمانی "
                          "(همان اصل قانون هب)."),
                _tool_row(ft.Icons.PALETTE,
                          "نوار پیشرفت چندرنگ: بازخورد بصری فوری که ترشح "
                          "دوپامین را با دیدن زنجیره‌ی موفقیت فعال می‌کند."),
                _tool_row(ft.Icons.RESTORE,
                          "روزهای جبرانی: مقابله با تفکر «همه یا هیچ» که "
                          "بزرگ‌ترین دشمن تداوم است."),
                _tool_row(ft.Icons.FLAG,
                          "افق ۴۰ روزه‌ی مشخص: هدف نزدیک و پایان‌پذیر، "
                          "پایبندی را افزایش می‌دهد."),
            ],
            spacing=8,
        ),
    )


def _references() -> ft.Control:
    refs = [
        "Hebb, D. O. (1949). The Organization of Behavior.",
        "Lally, P., van Jaarsveld, C. H. M., Potts, H. W. W., & Wardle, J. "
        "(2010). How are habits formed: Modelling habit formation in the real "
        "world. European Journal of Social Psychology, 40(6), 998–1009.",
        "Wood, W., & Neal, D. T. (2007). A new look at habits and the "
        "habit–goal interface. Psychological Review, 114(4), 843–863.",
        "Kleim, J. A., & Jones, T. A. (2008). Principles of "
        "experience-dependent neural plasticity. JSLHR, 51(1), S225–S239.",
    ]
    return _card(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.MENU_BOOK, size=16,
                                color=ft.Colors.GREY_500),
                        ft.Text("منابع", size=12, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.GREY_600),
                    ],
                    spacing=6,
                ),
                ft.Column(
                    [ft.Text("• " + r, size=9.5, color=ft.Colors.GREY_500)
                     for r in refs],
                    spacing=3,
                ),
            ],
            spacing=6,
        ),
    )


def build_science_view(app) -> ft.Control:
    """محتوای صفحه‌ی پشتوانه‌ی علمی (اسکرول را View مدیریت می‌کند)."""
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        content=ft.Column(
            [
                _hero(),
                _section(
                    "نوروپلاستیسیته — مغزِ در حال بازسازی",
                    "مغز اندامی ثابت نیست؛ شبکه‌ای زنده است که با تجربه بازسازی "
                    "می‌شود. اتصالات میان نورون‌ها (سیناپس‌ها) با استفاده تقویت و "
                    "با بی‌استفاده‌ای تضعیف می‌شوند. هر روزِ چله، در واقع یک "
                    "جلسه‌ی تمرین برای مدار عصبیِ رفتار جدید شماست.",
                    ft.Icons.AUTO_AWESOME, ACCENT,
                ),
                _section(
                    "قانون هب — «نورون‌هایی که با هم شلیک می‌کنند، با هم "
                    "سیم‌کشی می‌شوند»",
                    "وقتی هر روز در زمان و مکان مشخصی رفتار را انجام می‌دهید، "
                    "مغز نشانه‌های محیطی (ساعت روز، مکان، حالت درون) را با خودِ "
                    "رفتار پیوند می‌زند. کم‌کم همین نشانه‌ها به محرکِ انجام "
                    "رفتار تبدیل می‌شوند و دیگر به اراده‌ی خالص وابسته نیستید.",
                    ft.Icons.SYNC_ALT, "#00897B",
                ),
                _section(
                    "میلین — آسفالت‌کردن جاده‌ی عصبی",
                    "تکرار منظم، غلاف میلین (عایق چربی دور رشته‌های عصبی) را "
                    "در همان مسیر افزایش می‌دهد؛ درست مثل عایق‌کاری سیم برق. "
                    "سیگنال در مسیر میلین‌دار تا حدود ۱۰۰ برابر سریع‌تر و "
                    "دقیق‌تر منتقل می‌شود. هر تکرار روزانه، یک لایه آسفالت روی "
                    "جاده‌ی عصبی رفتار شماست.",
                    ft.Icons.BOLT, "#F57C00",
                ),
                _section(
                    "از اراده به خودکاری — انتقال کنترل به عقده‌های قاعده‌ای",
                    "انجام رفتار جدید ابتدا کار قشر پیش‌پیشانی است: مرکز "
                    "تصمیم و اراده؛ پرهزینه، کند و زودخسته. با تکرار کافی، "
                    "کنترل به عقده‌های قاعده‌ای در عمق مغز منتقل می‌شود — همان "
                    "ساختاری که عادت‌ها را به‌صورت خودکار ذخیره می‌کند. نتیجه: "
                    "اراده‌ی شما برای کارهای مهم‌تر آزاد می‌شود.",
                    ft.Icons.AUTORENEW, "#1976D2",
                ),
                _section(
                    "دوپامین — موتور انگیزه",
                    "هر ثبت موفق، سیستم پاداش مغز را فعال می‌کند. دوپامین فقط "
                    "هنگام لذت ترشح نمی‌شود؛ هنگام پیش‌بینی پاداش هم ترشح "
                    "می‌شود و موتور انگیزه است. تیک صبح و شب و دیدن زنجیره‌ی "
                    "روزهای موفق، همین حلقه را تغذیه می‌کند: انگیزه ← عمل ← "
                    "پاداش ← انگیزه‌ی بیشتر.",
                    ft.Icons.TRENDING_UP, "#2E7D32",
                ),
                _forty_days_section(),
                _tools_section(),
                _references(),
                ft.Text(
                    "محتوای این صفحه صرفاً جنبه‌ی آموزشی دارد و جایگزین "
                    "مشاوره‌ی پزشکی یا روان‌شناختی نیست.",
                    size=10, color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=12,
        ),
    )