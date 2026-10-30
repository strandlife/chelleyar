import flet as ft

# ==================================================================
# صفحه‌ی پشتوانه‌ی علمی — نوروپلاستیسیته و سازوکار عادت
# ==================================================================

ACCENT  = "#5C6BC0"
PURPLE  = "#7B1FA2"
GREEN   = "#2E7D32"
ORANGE  = "#F57C00"
TEAL    = "#00897B"
BLUE    = "#1976D2"
ROSE    = "#C2185B"
GREYISH = "#78909C"

# رنگ‌های سمانتیک تا در تم روشن و تیره هر دو خوانا باشند
INK   = ft.Colors.ON_SURFACE_VARIANT
MUTED = ft.Colors.OUTLINE


# ------------------------------------------------------------------
# اجزای پایه
# ------------------------------------------------------------------

def _card(content: ft.Control, padding: int = 14, key=None) -> ft.Container:
    """کارت استاندارد — هم‌سبک با کارت‌های چله."""
    return ft.Container(
        content=content,
        key=key,
        padding=ft.Padding.all(padding),
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
    )


def _icon_box(icon, color, size=22, box=44, radius=12) -> ft.Container:
    return ft.Container(
        content=ft.Icon(icon, color=color, size=size),
        width=box, height=box,
        bgcolor=ft.Colors.with_opacity(0.12, color),
        border_radius=radius,
        alignment=ft.Alignment.CENTER,
    )


def _section_header(icon, color, title, size=13.5) -> ft.Row:
    return ft.Row(
        [
            _icon_box(icon, color, size=16, box=30, radius=9),
            ft.Text(title, size=size, weight=ft.FontWeight.BOLD, expand=True),
        ],
        spacing=10,
    )


def _body(text, size=12) -> ft.Text:
    return ft.Text(text, size=size, color=INK, text_align=ft.TextAlign.START)


def _tip(text) -> ft.Container:
    """جعبه‌ی «در عمل» — پیوند علم با کاری که همین حالا می‌شود کرد."""
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.LIGHTBULB, size=14, color=ORANGE),
                ft.Text("در عمل: " + text, size=11, color=INK,
                        text_align=ft.TextAlign.START, expand=True),
            ],
            spacing=6,
        ),
        padding=ft.Padding.all(10),
        bgcolor=ft.Colors.with_opacity(0.10, ORANGE),
        border_radius=10,
    )


def _expander(registry, number, title, summary, body_controls, icon, color,
              expanded=False) -> ft.Container:
    """کارت بازشدنیِ سبک — خلاصه جلوی عنوان، متن کامل با کلیک.

    registry  : لیستی که تابع set_state داخلش ثبت می‌شود (برای «باز/بستن همه»)؛
                None یعنی مستقل است.
    """
    state = {"open": expanded}
    chev = ft.Icon(
        ft.Icons.KEYBOARD_ARROW_UP if expanded else ft.Icons.KEYBOARD_ARROW_DOWN,
        size=20, color=color,
    )
    body = ft.Container(
        content=ft.Column(body_controls, spacing=8),
        padding=ft.Padding(12, 2, 12, 12),
        visible=expanded,
    )

    def set_state(open_):
        state["open"] = open_
        body.visible = open_
        chev.name = ft.Icons.KEYBOARD_ARROW_UP if open_ else ft.Icons.KEYBOARD_ARROW_DOWN

    if registry is not None:
        registry.append(set_state)

    def _toggle(e=None):
        set_state(not state["open"])
        try:
            body.update()
            chev.update()
        except Exception:
            pass

    head_items = []
    if number:
        head_items.append(
            ft.Container(
                content=ft.Text(number, size=9.5, weight=ft.FontWeight.BOLD,
                                color=color),
                padding=ft.Padding.symmetric(horizontal=7, vertical=2),
                bgcolor=ft.Colors.with_opacity(0.12, color),
                border_radius=8,
            )
        )
    head_items.append(
        ft.Column(
            [
                ft.Text(title, size=13, weight=ft.FontWeight.BOLD),
                *([ft.Text(summary, size=11, color=MUTED,
                           text_align=ft.TextAlign.START)] if summary else []),
            ],
            spacing=2,
            expand=True,
        )
    )
    head_items.append(chev)

    return ft.Container(
        border=ft.Border.all(1, ft.Colors.with_opacity(0.10, ft.Colors.ON_SURFACE)),
        border_radius=14,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Column(
            [
                ft.Container(
                    on_click=_toggle,
                    ink=True,
                    padding=ft.Padding.all(10),
                    border_radius=14,
                    content=ft.Row(
                        [_icon_box(icon, color, size=18, box=38, radius=11)]
                        + head_items,
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ),
                body,
            ],
            spacing=0,
        ),
    )


# ------------------------------------------------------------------
# ۱) هیرو
# ------------------------------------------------------------------

def _hero() -> ft.Control:
    def pill(icon, text):
        return ft.Container(
            content=ft.Row(
                [ft.Icon(icon, size=11, color=ft.Colors.WHITE),
                 ft.Text(text, size=9.5, color=ft.Colors.WHITE)],
                spacing=4, tight=True,
            ),
            padding=ft.Padding.symmetric(horizontal=9, vertical=4),
            bgcolor=ft.Colors.with_opacity(0.20, ft.Colors.WHITE),
            border_radius=20,
        )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.PSYCHOLOGY, size=28, color=ft.Colors.WHITE),
                        ft.Text("چگونه ۴۰ روز، مغز را بازسازی می‌کند؟",
                                size=16, weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE, expand=True),
                    ],
                    spacing=8,
                ),
                ft.Text(
                    "چله‌نشینی سنت قدیمی است و علم امروز هم تأییدش می‌کند. وقتی یک "
                    "رفتار را هر روز تکرار می‌کنی، مسیر عصبی‌اش در مغز قوی‌تر "
                    "می‌شود؛ کم‌کم از «کاری که هر روز باید تصمیمش را بگیری» به "
                    "«کاری که خودبه‌خود انجام می‌شود» می‌رسد. این صفحه نشان "
                    "می‌دهد در این ۴۰ روز در مغزت چه می‌گذرد، هر مرحله چه حسی "
                    "دارد، و چرا هر روزِ ثبت‌شده یک قدم واقعی است، نه فقط یک تیک.",
                    size=12,
                    color=ft.Colors.with_opacity(0.92, ft.Colors.WHITE),
                    text_align=ft.TextAlign.START,
                ),
                ft.Row(
                    [
                        pill(ft.Icons.SCHEDULE, "زمان مطالعه: ~۵ دقیقه"),
                        pill(ft.Icons.MENU_BOOK, "۶ منبع علمی"),
                    ],
                    spacing=6,
                ),
            ],
            spacing=10,
        ),
        padding=ft.Padding.all(16),
        border_radius=16,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_RIGHT,
            end=ft.Alignment.BOTTOM_LEFT,
            colors=["#5C6BC0", "#7E57C2"],
        ),
    )


# ------------------------------------------------------------------
# ۲) فهرست سریع
# ------------------------------------------------------------------

def _toc(app, items) -> ft.Control:
    page = getattr(app, "page", app)

    def _go(key):
        def handler(e):
            try:
                page.scroll_to(key=key, duration=400)
            except Exception:
                pass
        return handler

    chips = []
    for icon, label, key, color in items:
        chips.append(
            ft.Container(
                on_click=_go(key),
                ink=True,
                content=ft.Row(
                    [ft.Icon(icon, size=11, color=color),
                     ft.Text(label, size=10.5, color=color,
                             weight=ft.FontWeight.W_500)],
                    spacing=4, tight=True,
                ),
                padding=ft.Padding.symmetric(horizontal=9, vertical=6),
                bgcolor=ft.Colors.with_opacity(0.09, color),
                border_radius=20,
            )
        )
    return ft.Column(
        [
            ft.Text("در این صفحه", size=10.5, color=MUTED,
                    weight=ft.FontWeight.BOLD),
            ft.Row(chips, spacing=8, scroll=ft.ScrollMode.AUTO),
        ],
        spacing=6,
    )


# ------------------------------------------------------------------
# ۳) نقشه‌ی ۴۰ روز در یک نگاه
# ------------------------------------------------------------------

def _timeline_section() -> ft.Control:
    phases = [
        ("روز ۱ تا ۱۰", "دوران مقاومت",
         "کار هنوز دستِ قشر پیش‌پیشانی است؛ اراده مصرف می‌شود و سخت‌گذراندنش طبیعی است.",
         ROSE, ft.Icons.LOCAL_FIRE_DEPARTMENT),
        ("روز ۱۱ تا ۲۵", "دوران تبدیل",
         "اتصال‌های عصبی محکم می‌شوند و میلین ساخته می‌شود؛ کار کم‌کم سبک‌تر حس می‌شود.",
         ORANGE, ft.Icons.CHANGE_CIRCLE),
        ("روز ۲۶ تا ۴۰", "دوران خودکاری",
         "رفتار به شبکه‌ی عمیق‌تر مغز سپرده می‌شود؛ شروع کردن راحت‌تر از تصمیم گرفتن است.",
         GREEN, ft.Icons.ROCKET_LAUNCH),
    ]
    bar = ft.Container(
        content=ft.Row(
            [
                ft.Container(bgcolor=ROSE, expand=10),
                ft.Container(bgcolor=ORANGE, expand=15),
                ft.Container(bgcolor=GREEN, expand=15),
            ],
            spacing=0,
        ),
        height=10,
        border_radius=5,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )
    cards = []
    for days, title, desc, color, icon in phases:
        cards.append(
            ft.Container(
                expand=True,
                padding=ft.Padding.all(10),
                bgcolor=ft.Colors.with_opacity(0.07, color),
                border_radius=12,
                content=ft.Column(
                    [
                        ft.Row(
                            [ft.Icon(icon, size=13, color=color),
                             ft.Text(days, size=10.5, weight=ft.FontWeight.BOLD,
                                     color=color)],
                            spacing=5,
                        ),
                        ft.Text(title, size=12.5, weight=ft.FontWeight.BOLD),
                        ft.Text(desc, size=10.5, color=INK,
                                text_align=ft.TextAlign.START),
                    ],
                    spacing=5,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                ),
            )
        )
    return _card(
        ft.Column(
            [
                _section_header(ft.Icons.TIMELINE, PURPLE,
                                "نقشه‌ی ۴۰ روز در یک نگاه"),
                ft.Text(
                    "مغز در طول مسیر سه فاز متفاوت را طی می‌کند. دانستن جای "
                    "فعلی‌ات، نگرانیِ «چرا هنوز خودکار نشده؟» را کم می‌کند.",
                    size=11, color=MUTED, text_align=ft.TextAlign.START,
                ),
                bar,
                ft.Row(cards, spacing=8,
                       vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Text(
                    "این بازه‌ها آستانه‌اند نه قانون؛ سرعت هر مغز به فرد و نوع "
                    "رفتارش بستگی دارد.",
                    size=10, color=MUTED, text_align=ft.TextAlign.START,
                ),
            ],
            spacing=10,
        ),
        key="sec-timeline",
    )


# ------------------------------------------------------------------
# ۴) چرخه‌ی عادت
# ------------------------------------------------------------------

def _loop_section() -> ft.Control:
    steps = [
        ("نشانه", "زمان و مکانِ ثابت", ft.Icons.ALARM, TEAL),
        ("رفتار", "تمرین روزانه", ft.Icons.DIRECTIONS_RUN, ACCENT),
        ("پاداش", "تیک و زنجیره", ft.Icons.EMOJI_EVENTS, ORANGE),
        ("تکرار", "مسیر قوی‌تر", ft.Icons.ALL_INCLUSIVE, GREEN),
    ]
    row_items = []
    for i, (title, sub, icon, color) in enumerate(steps):
        row_items.append(
            ft.Column(
                [
                    _icon_box(icon, color, size=17, box=38, radius=19),
                    ft.Text(title, size=11.5, weight=ft.FontWeight.BOLD),
                    ft.Text(sub, size=9.5, color=MUTED,
                            text_align=ft.TextAlign.CENTER),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
                expand=True,
            )
        )
        if i < len(steps) - 1:
            row_items.append(ft.Icon(ft.Icons.ARROW_BACK, size=14, color=MUTED))

    return _card(
        ft.Column(
            [
                _section_header(ft.Icons.ALL_INCLUSIVE, TEAL,
                                "چرخه‌ی عادت — موتوری که خودش می‌چرخد"),
                _body(
                    "پژوهش‌های عادت می‌گویند هر عادت یک حلقه است: نشانه، رفتار، "
                    "پاداش. هر بار این حلقه کامل شود، مغز آن را در شبکه‌ی عادت "
                    "ذخیره می‌کند تا دفعه‌ی بعد بدون تصمیم‌گیری اجرایش کند "
                    "(Wood و Neal، ۲۰۰۷)."
                ),
                ft.Row(row_items, spacing=4,
                       vertical_alignment=ft.CrossAxisAlignment.START),
                _tip("در چله، نشانه‌ی تو ساعتِ ثبت است، رفتار انجامِ تمرین، و "
                     "پاداش تیک صبح و شب و دیدنِ زنجیره‌ی رنگی."),
            ],
            spacing=10,
        ),
        key="sec-loop",
    )


# ------------------------------------------------------------------
# ۵) عمق ماجرا — موضوع به موضوع (آکاردئون)
# ------------------------------------------------------------------

def _science_section(registry, page) -> ft.Control:
    def _set_all(open_):
        for set_state in registry:
            set_state(open_)
        try:
            page.update()
        except Exception:
            pass

    topics = [
        (
            "۰۱", "نوروپلاستیسیته — مغز همیشه در حال تغییر",
            "مغز با هر تجربه کمی عوض می‌شود؛ تکرار، اتصال‌های مرتبط را محکم‌تر می‌کند.",
            "تا چند دهه پیش فکر می‌کردند مغز بعد از کودکی دیگر تغییر نمی‌کند؛ "
            "حالا می‌دانیم اشتباه می‌کردند. مغز با هر تجربه کمی عوض می‌شود: "
            "وقتی کاری را انجام می‌دهی، اتصال‌های مربوط به همان کار محکم‌تر "
            "می‌شوند و وقتی رهایش می‌کنی، کم‌رنگ. پس هر روزِ چله یک جلسه‌ی "
            "تمرین واقعی برای رفتار جدیدت است.",
            "هر ثبت روزانه، یک جلسه‌ی تمرین واقعی برای مغز است — حتی روزهایی "
            "که حالت خوب نیست.",
            ft.Icons.AUTO_AWESOME, ACCENT, True,
        ),
        (
            "۰۲", "قانون هب — با هم فعال شوند، با هم قوی می‌شوند",
            "زمان و مکانِ ثابت، مغز را خودبه‌خود آماده‌ی کار می‌کند.",
            "هر بار که رفتاری را در زمان و مکان مشخصی انجام می‌دهی، مغز آن زمان "
            "و مکان را به خودِ رفتار گره می‌زند. مثلاً اگر هر روز ساعت ۶ صبح "
            "پیاده‌روی کنی، خودِ ساعت ۶ صبح به پیاده‌روی فکر می‌اندازد. بعد از "
            "مدتی لازم نیست هر روز تصمیم تازه بگیری؛ نشانه‌ها کار را شروع "
            "می‌کنند.",
            "ثبت صبح و شب را به ساعت و مکان مشخص گره بزن؛ بعد از مدتی خودِ "
            "نشانه کار را راه می‌اندازد.",
            ft.Icons.SYNC_ALT, TEAL, False,
        ),
        (
            "۰۳", "میلین — جاده‌ای که هر روز هموارتر می‌شود",
            "هر تکرار، پوشش مسیر عصبی را کلفت‌تر و پیام را سریع‌تر می‌کند.",
            "پیام‌های مغز روی مسیرهایی حرکت می‌کنند که دورشان لایه‌ای چربی به "
            "نام میلین پیچیده شده. هرچه این لایه کلفت‌تر باشد، پیام سریع‌تر و "
            "دقیق‌تر رد می‌شود؛ تا حدود ۱۰۰ برابر. تکرار روزانه دقیقاً همین کار "
            "را می‌کند؛ مثل جاده‌ای خاکی که هر روز کمی هموارتر می‌شود.",
            "تکرارِ منظمِ روزانه از تلاش‌های سنگینِ پراکنده مؤثرتر است؛ کیفیتِ "
            "استمرار مهم‌تر از شدت است.",
            ft.Icons.BOLT, ORANGE, False,
        ),
        (
            "۰۴", "از اراده به خودکاری — کار را به عمق مغز بسپار",
            "با تکرار، کار از قشر تصمیم‌گیر به شبکه‌ی عادت منتقل می‌شود.",
            "روزهای اول، کار سخت با قشر پیش‌پیشانی است؛ همان بخشی که تصمیم "
            "می‌گیرد و سریع خسته می‌شود — همان‌جا که بیشترِ انگیزه‌ها تمام "
            "می‌شود. اما با تکرار، مغز کار را به بخش عمیق‌تری می‌سپارد که "
            "عادت‌ها در آن ذخیره می‌شوند؛ آنجا دیگر کاری به انگیزه و اراده "
            "نیست. نتیجه؟ کاری که قبلاً به زور انجام می‌شد، حالا خودبه‌خود "
            "انجام می‌شود و اراده‌ات برای کارهای مهم‌تر آزاد می‌ماند.",
            "سختیِ دو هفته‌ی اول یعنی بار هنوز روی قشر پیش‌پیشانی است؛ طبیعی "
            "است و تمام می‌شود. به خودت سخت نگیر.",
            ft.Icons.AUTORENEW, BLUE, False,
        ),
        (
            "۰۵", "دوپامین — موتور انگیزه",
            "دوپامین بیشتر موقع پیش‌بینی پاداش ترشح می‌شود تا موقع رسیدن به آن.",
            "دوپامین فقط «شیمی لذت» نیست. این ماده بیشتر موقع پیش‌بینی پاداش "
            "ترشح می‌شود تا موقع رسیدن به آن؛ همان لحظه‌ای که به تو انگیزه "
            "می‌دهد بلند شوی و شروع کنی. تیک صبح و شب و دیدن زنجیره‌ی رنگی "
            "روزهای موفق دقیقاً همین حلقه را فعال نگه می‌دارد: انگیزه، عمل، "
            "بازخورد، و انگیزه‌ی بیشتر (Schultz، ۱۹۹۸).",
            "بعد از هر ثبت، یک لحظه زنجیره‌ات را نگاه کن؛ دیدنِ پیشرفت، پاداشِ "
            "کوچکی است که حلقه را روشن نگه می‌دارد.",
            ft.Icons.TRENDING_UP, GREEN, False,
        ),
    ]
    tiles = [
        _expander(registry, n, t, s, [_body(p), _tip(tip)], icon, color, exp)
        for n, t, s, p, tip, icon, color, exp in topics
    ]
    return _card(
        ft.Column(
            [
                _section_header(ft.Icons.SCIENCE, ACCENT, "عمق ماجرا — موضوع به موضوع"),
                ft.Text(
                    "جلوی هر موضوع یک خلاصه‌ی یک‌خطی هست؛ هر کدام را خواستی باز کن و بخوان.",
                    size=10.5, color=MUTED, text_align=ft.TextAlign.START,
                ),
                *tiles,
                ft.Row(
                    [
                        ft.TextButton("باز کردن همه", icon=ft.Icons.UNFOLD_MORE,
                                      on_click=lambda e: _set_all(True)),
                        ft.TextButton("بستن همه", icon=ft.Icons.UNFOLD_LESS,
                                      on_click=lambda e: _set_all(False)),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                ),
            ],
            spacing=10,
        ),
        key="sec-science",
    )


# ------------------------------------------------------------------
# ۶) اعداد کلیدی
# ------------------------------------------------------------------

def _stat_chip(value: str, label: str, color: str) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(value, size=14, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(label, size=10, color=MUTED,
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


def _numbers_section() -> ft.Control:
    return _card(
        ft.Column(
            [
                _section_header(ft.Icons.INSIGHTS, BLUE, "اعداد واقعی درباره‌ی عادت"),
                ft.Row(
                    [
                        _stat_chip("۶۶ روز", "میانگین خودکار شدن\nرفتار جدید", PURPLE),
                        _stat_chip("۱۸ تا ۲۵۴", "بازه‌ی فردی در\nپژوهش‌ها", ACCENT),
                        _stat_chip("۴۰ روز", "آستانه‌ی تعهد\nدر چله", GREEN),
                    ],
                    spacing=8,
                ),
                _body(
                    "«۲۱ روز کافی است» یک افسانه است. در پژوهشی معروف (Lally و "
                    "همکاران، ۲۰۱۰) مشخص شد خودکار شدن رفتار در هر فرد زمان "
                    "متفاوتی می‌برد؛ میانگینش ۶۶ روز و بازه‌اش ۱۸ تا ۲۵۴ روز "
                    "است. عدد ۴۰ هم جادو نیست؛ آستانه‌ای است به‌اندازه‌ی کافی "
                    "بلند که عادت جا بیفتد و به‌اندازه‌ی کافی روشن و پایان‌دار "
                    "که دلسرد نشوی. سنت چله‌نشینی قرن‌ها پیش از علم به همین "
                    "عدد رسیده بود."
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.VERIFIED, size=14, color=GREEN),
                            ft.Text(
                                "خبر خوب: در همان پژوهش، جا ماندنِ یک روز روند "
                                "عادت را خراب نکرد. عادت با سخت‌گیری ساخته "
                                "نمی‌شود؛ با ادامه دادن.",
                                size=11, color=INK,
                                text_align=ft.TextAlign.START, expand=True,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=ft.Padding.all(10),
                    bgcolor=ft.Colors.with_opacity(0.10, GREEN),
                    border_radius=10,
                ),
            ],
            spacing=10,
        ),
        key="sec-numbers",
    )


# ------------------------------------------------------------------
# ۷) افسانه و واقعیت
# ------------------------------------------------------------------

def _tag(text, color) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=9, weight=ft.FontWeight.BOLD, color=color),
        padding=ft.Padding.symmetric(horizontal=7, vertical=2),
        bgcolor=ft.Colors.with_opacity(0.14, color),
        border_radius=8,
    )


def _myth_item(myth: str, fact: str) -> ft.Container:
    return ft.Container(
        padding=ft.Padding.all(10),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.10, ft.Colors.ON_SURFACE)),
        border_radius=12,
        content=ft.Column(
            [
                ft.Row(
                    [_tag("افسانه", ROSE),
                     ft.Text(myth, size=11.5, color=MUTED, italic=True,
                             text_align=ft.TextAlign.START, expand=True)],
                    spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    [_tag("واقعیت", GREEN),
                     ft.Text(fact, size=11.5, color=INK,
                             text_align=ft.TextAlign.START, expand=True)],
                    spacing=8, vertical_alignment=ft.CrossAxisAlignment.START,
                ),
            ],
            spacing=6,
        ),
    )


def _myths_section() -> ft.Control:
    items = [
        ("۲۱ روز کافی است تا رفتار خودکار شود.",
         "میانگین واقعی ۶۶ روز است و بسته به فرد و نوع رفتار تا ۲۵۴ روز هم کش "
         "می‌آید. عدد ۴۰ یک آستانه‌ی خوب و پایان‌دار است، نه یک قانون جادویی."),
        ("همه‌چیز به اراده بستگی دارد؛ قوی باش!",
         "بخش بزرگی از رفتار به نشانه‌ها و محیط گره خورده است. زمان و مکانِ "
         "ثابت، نیمی از بارِ اراده را برمی‌دارد."),
        ("اگر انگیزه‌ام کم شود، یعنی شکست خورده‌ام.",
         "انگیزه ذاتاً نوسان دارد. سیستم‌هایی مثل ثبت صبح و شب و زنجیره‌ی "
         "رنگی، همین روزهای کم‌انگیزه را هم پوشش می‌دهند."),
        ("عادت‌های خوب شانسی شکل می‌گیرند.",
         "عادت نتیجه‌ی طراحی است، نه شانس: نشانه‌ی مشخص + تکرار روزانه + "
         "بازخورد دیدنی = مسیر عصبی قوی‌تر."),
    ]
    return _card(
        ft.Column(
            [
                _section_header(ft.Icons.RULE, ROSE, "افسانه و واقعیت"),
                *[_myth_item(m, f) for m, f in items],
            ],
            spacing=8,
        ),
        key="sec-myths",
    )


# ------------------------------------------------------------------
# ۸) قابلیت‌ها
# ------------------------------------------------------------------

def _tool_row(icon, text) -> ft.Row:
    return ft.Row(
        [
            ft.Icon(icon, size=15, color=ACCENT),
            ft.Text(text, size=11.5, color=INK,
                    text_align=ft.TextAlign.START, expand=True),
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.START,
    )


def _tools_section() -> ft.Control:
    rows = [
        (ft.Icons.LAYERS, "سطح‌بندی روزانه — در روزهای سخت هم بردِ کوچک ممکن "
                          "است؛ پس زنجیره‌ی پاداش قطع نمی‌شود."),
        (ft.Icons.SCHEDULE, "ثبت صبح و شب — رفتار به زمان‌های مشخص گره می‌خورد؛ "
                            "همان قانون هب، این‌بار در عمل."),
        (ft.Icons.PALETTE, "نوار پیشرفت چندرنگ — دیدن پیشرفت بازخورد فوری است "
                           "و حلقه‌ی دوپامین را روشن نگه می‌دارد."),
        (ft.Icons.RESTORE, "روزهای جبرانی — فکرِ «همه یا هیچ» بزرگ‌ترین دشمن "
                           "تداوم است؛ جبران این فکر را می‌شکند."),
        (ft.Icons.FLAG, "افق ۴۰ روزه — هدفِ نزدیک و پایان‌دار، ذهن را راحت و "
                        "پای‌کار نگه می‌دارد."),
    ]
    return _card(
        ft.Column(
            [
                _section_header(ft.Icons.FACT_CHECK, ACCENT,
                                "این قابلیت‌ها تزئینی نیستند"),
                ft.Text(
                    "هر ابزارِ چله، یک اصل علمی از همین صفحه را در عمل اجرا می‌کند:",
                    size=10.5, color=MUTED, text_align=ft.TextAlign.START,
                ),
                *[_tool_row(i, t) for i, t in rows],
            ],
            spacing=8,
        ),
        key="sec-tools",
    )


# ------------------------------------------------------------------
# ۹) پرسش‌های پرتکرار
# ------------------------------------------------------------------

def _faq_section() -> ft.Control:
    faqs = [
        ("یک روز را جا انداختم؛ چله‌ام خراب شد؟",
         "نه. در پژوهش Lally، یک روزِ جاافتادن اثر معناداری روی روند خودکار "
         "شدن نداشت. از روز جبرانی استفاده کن و ادامه بده. فقط مواظب باش "
         "دوباره‌ی پشت‌سرهم نشود؛ دو روزِ پشت‌سرهم شانسِ رها کردن را جدی بالا "
         "می‌برد."),
        ("چرا روزهای اول این‌قدر سخت است؟",
         "چون کار هنوز روی دوش قشر پیش‌پیشانی است؛ بخشی که تصمیم می‌گیرد و "
         "سریع خسته می‌شود. سختیِ اولِ راه یعنی تمرین دارد انجام می‌شود؛ از "
         "میانه‌ی راه کم‌کم سبک‌تر می‌شود."),
        ("وسط راه بی‌حس و تکراری می‌شود؛ طبیعی است؟",
         "بله؛ به این «فلات میانه» می‌گویند. پیشرفت زیرِ سطح ادامه دارد ولی "
         "دیده نمی‌شود. در این روزها به احساست نگاه نکن، به زنجیره‌ات نگاه "
         "کن. ضمناً هرچه به خط پایان نزدیک‌تر شوی، پیشرفت دوباره بیشتر حس "
         "می‌شود؛ این را «اثر گرادیان هدف» می‌نامند."),
        ("بعد از روزِ چهلم چه می‌شود؟",
         "چهلم پایان مسیر نیست؛ نقطه‌ی تحویل است. رفتار از حالت «تلاش روزانه» "
         "به حالت «عادت» نزدیک شده و ادامه‌اش هزینه‌ی ذهنی خیلی کمتری دارد. "
         "اگر خواستی، چله‌ی بعدی را با یک هدف تازه شروع کن."),
    ]
    tiles = [
        _expander(None, None, q, None, [_body(a)],
                  ft.Icons.HELP_OUTLINE, ORANGE, False)
        for q, a in faqs
    ]
    return _card(
        ft.Column(
            [
                _section_header(ft.Icons.HELP_OUTLINE, ORANGE, "پرسش‌های پرتکرار"),
                *tiles,
            ],
            spacing=8,
        ),
        key="sec-faq",
    )


# ------------------------------------------------------------------
# ۱۰) منابع
# ------------------------------------------------------------------

def _references(registry) -> ft.Control:
    refs = [
        "Hebb, D. O. (1949). The Organization of Behavior. New York: Wiley.",
        "Lally, P., van Jaarsveld, C. H. M., Potts, H. W. W., & Wardle, J. "
        "(2010). How are habits formed: Modelling habit formation in the real "
        "world. European Journal of Social Psychology, 40(6), 998–1009.",
        "Wood, W., & Neal, D. T. (2007). A new look at habits and the "
        "habit–goal interface. Psychological Review, 114(4), 843–863.",
        "Kleim, J. A., & Jones, T. A. (2008). Principles of "
        "experience-dependent neural plasticity: Implications for "
        "rehabilitation after brain damage. JSLHR, 51(1), S225–S239.",
        "Schultz, W. (1998). Predictive reward signal of dopamine neurons. "
        "Journal of Neurophysiology, 80(1), 1–27.",
        "Gollwitzer, P. M. (1999). Implementation intentions: Strong effects "
        "of simple plans. American Psychologist, 54(7), 493–503.",
    ]
    body = [
        ft.Row(
            [
                ft.Text(f"{i + 1}.", size=10, weight=ft.FontWeight.BOLD,
                        color=MUTED),
                ft.Text(r, size=10, color=MUTED,
                        text_align=ft.TextAlign.START, expand=True),
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        for i, r in enumerate(refs)
    ]
    return _card(
        _expander(
            registry, None, "منابع علمی",
            "هر ادعای این صفحه به یکی از این ۶ منبع وصل است.",
            body, ft.Icons.MENU_BOOK, GREYISH, False,
        ),
        key="sec-refs",
    )


# ------------------------------------------------------------------
# ۱۱) پایان‌بندی
# ------------------------------------------------------------------

def _closing() -> ft.Control:
    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(ft.Icons.FORMAT_QUOTE, size=20, color=ft.Colors.WHITE),
                ft.Text(
                    "چهل روز بعد، یک بار دیگر این صفحه را بخوان؛ این‌بار نه "
                    "برای یاد گرفتن، برای مقایسه‌ی خودت با دیروز.",
                    size=12, color=ft.Colors.WHITE, italic=True,
                    text_align=ft.TextAlign.START, expand=True,
                ),
            ],
            spacing=10,
        ),
        padding=ft.Padding.all(14),
        border_radius=16,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.BOTTOM_RIGHT,
            end=ft.Alignment.TOP_LEFT,
            colors=["#7E57C2", "#5C6BC0"],
        ),
    )


# ------------------------------------------------------------------
# مونتاژ نهایی
# ------------------------------------------------------------------

def build_science_view(app) -> ft.Control:
    """محتوای صفحه‌ی پشتوانه‌ی علمی (اسکرول را View مدیریت می‌کند)."""
    page = getattr(app, "page", app)
    science_registry: list = []
    refs_registry: list = []

    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
        content=ft.Column(
            [
                _hero(),
                _toc(
                    app,
                    [
                        (ft.Icons.TIMELINE, "نقشه‌ی ۴۰ روز", "sec-timeline", PURPLE),
                        (ft.Icons.ALL_INCLUSIVE, "چرخه‌ی عادت", "sec-loop", TEAL),
                        (ft.Icons.SCIENCE, "عمق علم", "sec-science", ACCENT),
                        (ft.Icons.INSIGHTS, "اعداد کلیدی", "sec-numbers", BLUE),
                        (ft.Icons.RULE, "افسانه و واقعیت", "sec-myths", ROSE),
                        (ft.Icons.HELP_OUTLINE, "پرسش‌ها", "sec-faq", ORANGE),
                        (ft.Icons.MENU_BOOK, "منابع", "sec-refs", GREYISH),
                    ],
                ),
                _timeline_section(),
                _loop_section(),
                _science_section(science_registry, page),
                _numbers_section(),
                _myths_section(),
                _tools_section(),
                _faq_section(),
                _references(refs_registry),
                _closing(),
                ft.Row(
                    [
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=12, color=MUTED),
                        ft.Text(
                            "محتوای این صفحه آموزشی است و جایگزین مشاوره‌ی "
                            "پزشکی یا روان‌شناختی نیست.",
                            size=10, color=MUTED,
                            text_align=ft.TextAlign.CENTER, expand=True,
                        ),
                    ],
                    spacing=4,
                ),
            ],
            spacing=12,
        ),
    )