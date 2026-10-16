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
                        ft.Text(title, size=14, weight=ft.FontWeight.BOLD,
                                expand=True),
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
                    "چله‌نشینی سنت قدیمی است و علم امروز هم تأییدش می‌کند. "
                    "وقتی یک رفتار را هر روز تکرار می‌کنی، مسیر عصبی‌اش در "
                    "مغز قوی‌تر می‌شود. کم‌کم آن رفتار از «کاری که هر روز "
                    "باید تصمیمش را بگیری» به «کاری که خود به خود انجام "
                    "می‌شود» می‌رسد. در ادامه می‌بینی در این ۴۰ روز در مغزت "
                    "چه می‌گذرد، و چرا هر روزِ ثبت‌شده یک قدم واقعی است، نه "
                    "فقط یک تیک.",
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
                ft.Text(label, size=10, color=ft.Colors.GREY_600,
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
                        ft.Text("چرا ۴۰ روز؟ (پاسخ صادقانه)",
                                size=13.5, weight=ft.FontWeight.BOLD,
                                expand=True),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "«۲۱ روز کافی است» یک افسانه است. در پژوهشی معروف "
                    "(Lally و همکاران، ۲۰۱۰) مشخص شد خودکار شدن رفتار در هر "
                    "فردی زمان متفاوتی می‌برد. میانگینش را پایین‌تر می‌بینی. "
                    "عدد ۴۰ هم جادو نیست؛ یک آستانه‌ی خوب است. به اندازه‌ای "
                    "بلند که عادت جا بیفتد، و به اندازه‌ای روشن و پایان‌دار "
                    "که دلسرد نشوی. سنت چله‌نشینی قرن‌ها پیش از علم به همین "
                    "عدد رسیده بود.",
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
                    "خبر خوب: در همان پژوهش، جا ماندن یک روز روند عادت را خراب "
                    "نکرد. عادت با سخت‌گیری ساخته نمی‌شود؛ با ادامه دادن. پس "
                    "روز جامانده پایان راه نیست. جبرانش کن و ادامه بده.",
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
                        ft.Text("این قابلیت‌ها تزئینی نیستند",
                                size=13.5, weight=ft.FontWeight.BOLD,
                                expand=True),
                    ],
                    spacing=8,
                ),
                _tool_row(ft.Icons.LAYERS,
                          "سطح‌بندی روزانه — در روزهای سخت هم برد کوچک ممکن "
                          "است. پس زنجیره‌ی پاداش قطع نمی‌شود."),
                _tool_row(ft.Icons.SCHEDULE,
                          "ثبت صبح و شب — رفتار به زمان‌های مشخص گره می‌خورد. "
                          "همان قانون هب، این‌بار در عمل."),
                _tool_row(ft.Icons.PALETTE,
                          "نوار پیشرفت چندرنگ — دیدن پیشرفت، بازخورد فوری "
                          "است و انگیزه را روشن نگه می‌دارد."),
                _tool_row(ft.Icons.RESTORE,
                          "روزهای جبرانی — فکر «همه یا هیچ» بزرگ‌ترین دشمن "
                          "تداوم است. جبران این فکر را می‌شکند."),
                _tool_row(ft.Icons.FLAG,
                          "افق ۴۰ روزه — هدفی نزدیک و پایان‌دار، ذهن را "
                          "راحت و پای‌کار نگه می‌دارد."),
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
                    [ft.Text("• " + r, size=10, color=ft.Colors.GREY_500)
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
                    "نوروپلاستیسیته — مغز همیشه در حال تغییر",
                    "تا چند دهه پیش فکر می‌کردند مغز بعد از کودکی دیگر تغییر "
                    "نمی‌کند. حالا می‌دانیم اشتباه می‌کردند. مغز با هر تجربه "
                    "کمی عوض می‌شود. وقتی کاری را انجام می‌دهی، اتصال‌های "
                    "مربوط به همان کار محکم‌تر می‌شوند. وقتی کاری را رها "
                    "می‌کنی، کم‌رنگ می‌شوند. پس هر روز چله، یک جلسه تمرین "
                    "واقعی برای رفتار جدیدت است.",
                    ft.Icons.AUTO_AWESOME, ACCENT,
                ),
                _section(
                    "قانون هب — نورون‌هایی که با هم کار می‌کنند، با هم قوی "
                    "می‌شوند",
                    "یعنی چه؟ هر بار که رفتاری را در زمان و مکان مشخصی انجام "
                    "می‌دهی، مغز آن زمان و مکان را به خودِ رفتار گره می‌زند. "
                    "مثلاً اگر هر روز ساعت ۶ صبح پیاده‌روی کنی، خودِ ساعت ۶ "
                    "صبح کم‌کم به پیاده‌روی فکر می‌اندازد. بعد از مدتی لازم "
                    "نیست هر روز تصمیم تازه بگیری؛ نشانه‌ها کار را شروع "
                    "می‌کنند.",
                    ft.Icons.SYNC_ALT, "#00897B",
                ),
                _section(
                    "میلین — جاده‌ای که هر روز هموارتر می‌شود",
                    "پیام‌های مغز روی مسیرهایی حرکت می‌کنند که دورشان لایه‌ای "
                    "چربی به نام میلین پیچیده شده. هرچه این لایه کلفت‌تر "
                    "باشد، پیام سریع‌تر و دقیق‌تر رد می‌شود؛ تا حدود ۱۰۰ "
                    "برابر. تکرار روزانه دقیقاً همین کار را می‌کند. هر تکرار، "
                    "یک لایه به این پوشش اضافه می‌کند؛ مثل جاده‌ای خاکی که "
                    "هر روز کمی هموارتر می‌شود.",
                    ft.Icons.BOLT, "#F57C00",
                ),
                _section(
                    "از اراده به خودکاری — کار را به عمق مغز بسپار",
                    "روزهای اول، کار سخت با قشر پیش‌پیشانی مغز است؛ همان "
                    "بخشی که تصمیم می‌گیرد. این بخش سریع خسته می‌شود و "
                    "همین‌جاست که بیشتر انگیزه‌ها تمام می‌شود. اما با تکرار، "
                    "مغز این کار را به بخش عمیق‌تری می‌سپارد که عادت‌ها در "
                    "آن ذخیره می‌شوند. آنجا دیگر کاری به انگیزه و اراده "
                    "نیست. نتیجه؟ کاری که قبلاً به زور انجام می‌شد، حالا خود "
                    "به خود انجام می‌شود و اراده‌ات برای کارهای مهم‌تر آزاد "
                    "می‌ماند.",
                    ft.Icons.AUTORENEW, "#1976D2",
                ),
                _section(
                    "دوپامین — موتور انگیزه",
                    "دوپامین فقط «شیمی لذت» نیست. این ماده بیشتر موقع "
                    "پیش‌بینی پاداش ترشح می‌شود تا موقع رسیدن به آن؛ همان "
                    "لحظه‌ای که به تو انگیزه می‌دهد بلند شوی و شروع کنی. تیک "
                    "صبح و شب و دیدن زنجیره‌ی رنگی روزهای موفق، دقیقاً همین "
                    "حلقه را فعال نگه می‌دارد: انگیزه، عمل، بازخورد، و "
                    "انگیزه‌ی بیشتر.",
                    ft.Icons.TRENDING_UP, "#2E7D32",
                ),
                _forty_days_section(),
                _tools_section(),
                _references(),
                ft.Text(
                    "محتوای این صفحه آموزشی است و جایگزین مشاوره‌ی پزشکی یا "
                    "روان‌شناختی نیست.",
                    size=10, color=ft.Colors.GREY_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=12,
        ),
    )