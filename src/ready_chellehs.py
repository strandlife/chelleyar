"""چله‌های آماده: داده‌های قالبی + ویجت انتخاب"""

import flet as ft

from theme import elevated_card

# ---------- نوع‌های چله ----------
READY_TYPES = [
    {"key": "worship",      "title": "عبادت",     "icon": ft.Icons.SELF_IMPROVEMENT},
    {"key": "quran",        "title": "قرآن",      "icon": ft.Icons.MENU_BOOK},
    {"key": "sport",        "title": "ورزش",      "icon": ft.Icons.FITNESS_CENTER},
    {"key": "study",        "title": "مطالعه",    "icon": ft.Icons.SCHOOL},
    {"key": "habit",        "title": "ترک عادت",  "icon": ft.Icons.BLOCK},
    {"key": "health",       "title": "سلامت",     "icon": ft.Icons.FAVORITE},
    {"key": "productivity", "title": "بهره‌وری",  "icon": ft.Icons.WORK},
    {"key": "family",       "title": "خانواده",   "icon": ft.Icons.GROUPS},
]

# ---------- قالب‌های آماده (scoreها در هر قالب یکتا باشند) ----------
READY_TEMPLATES = {
    "worship": [
        {
            "key": "salat-sobh", "name": "چله نماز صبح",
            "display_name": "نماز صبح اول وقت",
            "task": "برخاستن برای نماز صبح و خواندن آن در اول وقت",
            "levels": [
                {"title": "پیش از ظهر خوانده شد", "score": 1, "color": "#9CCC65"},
                {"title": "در اول وقت", "score": 3, "color": "#43A047"},
                {"title": "اول وقت با حضور قلب", "score": 5, "color": "#1B5E20"},
            ],
        },
        {
            "key": "salat-vajeb", "name": "چله نمازهای واجب",
            "display_name": "پنج نماز اول وقت",
            "task": "خواندن نمازهای واجب روزانه در اول وقت و با توجه",
            "levels": [
                {"title": "همه نمازها در همان روز خوانده شد", "score": 1, "color": "#9CCC65"},
                {"title": "اکثر نمازها اول وقت", "score": 3, "color": "#43A047"},
                {"title": "هر پنج نماز اول وقت", "score": 5, "color": "#1B5E20"},
            ],
        },
        {
            "key": "namaz-shab", "name": "چله نماز شب",
            "display_name": "نماز شب",
            "task": "اقامه نماز شب پیش از اذان صبح",
            "levels": [
                {"title": "۳ رکعت وتر", "score": 1, "color": "#9CCC65"},
                {"title": "۵ رکعت", "score": 3, "color": "#43A047"},
                {"title": "۱۱ رکعت کامل", "score": 5, "color": "#1B5E20"},
            ],
        },
        {
            "key": "doa-ahd", "name": "چله دعای عهد",
            "display_name": "ملاقات با امام زمان (عج)",
            "task": "خواندن دعای عهد هر روز صبح",
            "levels": [
                {"title": "ادای مطلق دعا", "score": 1, "color": "#9CCC65"},
                {"title": "نشسته و با تمرکز", "score": 3, "color": "#43A047"},
                {"title": "ایستاده با حضور قلب", "score": 5, "color": "#1B5E20"},
            ],
        },
    ],
    "quran": [
        {
            "key": "khatm", "name": "چله ختم قرآن",
            "display_name": "ختم قرآن در ۴۰ روز",
            "task": "روزی ۲۰ صفحه تلاوت قرآن برای ختم یک دوره کامل در پایان چله",
            "levels": [
                {"title": "حداقل ۵ صفحه", "score": 1, "color": "#90CAF9"},
                {"title": "۲۰ صفحه تلاوت", "score": 3, "color": "#42A5F5"},
                {"title": "۲۰ صفحه با تدبر", "score": 5, "color": "#1565C0"},
            ],
        },
        {
            "key": "hefz", "name": "چله حفظ قرآن",
            "display_name": "حفظ روزانه آیات",
            "task": "حفظ روزانه آیات جدید همراه با مرور حفظ‌های قبلی",
            "levels": [
                {"title": "فقط مرور حفظ‌های قبلی", "score": 1, "color": "#90CAF9"},
                {"title": "۳ آیه جدید + مرور", "score": 3, "color": "#42A5F5"},
                {"title": "۵ آیه جدید + مرور کامل", "score": 5, "color": "#1565C0"},
            ],
        },
        {
            "key": "tadabbor", "name": "چله تدبر در قرآن",
            "display_name": "تدبر روزانه",
            "task": "روزی ۱۰ دقیقه تلاوت و مطالعه تفسیر آیات",
            "levels": [
                {"title": "چند آیه با ترجمه", "score": 1, "color": "#90CAF9"},
                {"title": "۱۰ دقیقه تلاوت و تفسیر", "score": 3, "color": "#42A5F5"},
                {"title": "تدبر + یادداشت نکته‌ها", "score": 5, "color": "#1565C0"},
            ],
        },
    ],
    "sport": [
        {
            "key": "walk", "name": "چله پیاده‌روی",
            "display_name": "پیاده‌روی روزانه",
            "task": "پیاده‌روی روزانه در هوای آزاد و چک کردن قدم‌شمار",
            "levels": [
                {"title": "۳٬۰۰۰ قدم", "score": 1, "color": "#FFCC80"},
                {"title": "۶٬۰۰۰ قدم", "score": 3, "color": "#FFA726"},
                {"title": "۱۰٬۰۰۰ قدم", "score": 5, "color": "#EF6C00"},
            ],
        },
        {
            "key": "badansazi", "name": "چله بدنسازی",
            "display_name": "تمرین روزانه بدنسازی",
            "task": "انجام تمرین طبق برنامه هفتگی با گرم‌کردن و سردکردن",
            "levels": [
                {"title": "۲۰ دقیقه تمرین سبک", "score": 1, "color": "#FFCC80"},
                {"title": "تمرین کامل روز", "score": 3, "color": "#FFA726"},
                {"title": "تمرین کامل + کششی/کاردیو", "score": 5, "color": "#EF6C00"},
            ],
        },
        {
            "key": "doidan", "name": "چله دویدن",
            "display_name": "دوی روزانه",
            "task": "دویدن آرام روزانه برای تقویت استقامت",
            "levels": [
                {"title": "۱ کیلومتر", "score": 1, "color": "#FFCC80"},
                {"title": "۲ کیلومتر", "score": 3, "color": "#FFA726"},
                {"title": "۳ کیلومتر یا بیشتر", "score": 5, "color": "#EF6C00"},
            ],
        },
    ],
    "study": [
        {
            "key": "ketabkhaani", "name": "چله کتاب‌خوانی",
            "display_name": "روزی ۳۰ صفحه کتاب",
            "task": "مطالعه روزانه کتاب (تخصصی یا عمومی) و یادداشت‌برداری",
            "levels": [
                {"title": "۱۰ صفحه", "score": 1, "color": "#B39DDB"},
                {"title": "۳۰ صفحه", "score": 3, "color": "#7E57C2"},
                {"title": "۳۰ صفحه + خلاصه", "score": 5, "color": "#4527A0"},
            ],
        },
        {
            "key": "zaban", "name": "چله زبان انگلیسی",
            "display_name": "انگلیسی هر روز",
            "task": "روزی ۱۰ لغت جدید و ۳۰ دقیقه تمرین شنیداری/گرامر",
            "levels": [
                {"title": "۵ لغت یا یک پادکست", "score": 1, "color": "#B39DDB"},
                {"title": "۱۰ لغت جدید", "score": 3, "color": "#7E57C2"},
                {"title": "۱۰ لغت + ۳۰ دقیقه تمرین", "score": 5, "color": "#4527A0"},
            ],
        },
        {
            "key": "darsi", "name": "چله مطالعه درسی",
            "display_name": "مطالعه درسی روزانه",
            "task": "مطالعه و مرور روزانه درس‌ها طبق برنامه",
            "levels": [
                {"title": "۱ ساعت مطالعه", "score": 1, "color": "#B39DDB"},
                {"title": "۲ ساعت مطالعه", "score": 3, "color": "#7E57C2"},
                {"title": "۳ ساعت با تمرین و تست", "score": 5, "color": "#4527A0"},
            ],
        },
    ],
    "habit": [
        {
            "key": "mobile", "name": "چله مهار موبایل",
            "display_name": "کاهش فضای مجازی",
            "task": "استفاده از موبایل و شبکه‌های اجتماعی فقط در زمان مشخص و ضروری",
            "levels": [
                {"title": "کمتر از ۲ ساعت", "score": 1, "color": "#B2DFDB"},
                {"title": "کمتر از ۱ ساعت", "score": 3, "color": "#4DB6AC"},
                {"title": "کمتر از ۳۰ دقیقه", "score": 5, "color": "#00695C"},
            ],
        },
        {
            "key": "ghand", "name": "چله ترک قند",
            "display_name": "دوری از قند و شیرینی",
            "task": "نخوردن قند، شیرینی، شکلات و نوشابه",
            "levels": [
                {"title": "مصرف خیلی کم", "score": 1, "color": "#B2DFDB"},
                {"title": "بدون نوشابه و شیرینی", "score": 3, "color": "#4DB6AC"},
                {"title": "روز کامل بدون قند", "score": 5, "color": "#00695C"},
            ],
        },
        {
            "key": "khab", "name": "چله خواب منظم",
            "display_name": "خواب و بیداری منظم",
            "task": "خواب پیش از ۲۳:۰۰ و بیداری پیش از ۶:۰۰",
            "levels": [
                {"title": "اختلاف کمتر از ۳۰ دقیقه با هدف", "score": 1, "color": "#B2DFDB"},
                {"title": "یکی از دو زمان رعایت شد", "score": 3, "color": "#4DB6AC"},
                {"title": "هر دو زمان رعایت شد", "score": 5, "color": "#00695C"},
            ],
        },
    ],
    "health": [
        {
            "key": "ab", "name": "چله آب کافی",
            "display_name": "روزی ۸ لیوان آب",
            "task": "نوشیدن حدود ۸ لیوان آب در طول روز",
            "levels": [
                {"title": "۴ لیوان", "score": 1, "color": "#81D4FA"},
                {"title": "۶ لیوان", "score": 3, "color": "#29B6F6"},
                {"title": "۸ لیوان و بیشتر", "score": 5, "color": "#0277BD"},
            ],
        },
        {
            "key": "taghzie", "name": "چله تغذیه سالم",
            "display_name": "تغذیه سالم",
            "task": "پرهیز از فست‌فود و افزودن میوه و سبزیجات به وعده‌ها",
            "levels": [
                {"title": "یک وعده سالم", "score": 1, "color": "#81D4FA"},
                {"title": "بدون فست‌فود", "score": 3, "color": "#29B6F6"},
                {"title": "تمام وعده‌ها سالم", "score": 5, "color": "#0277BD"},
            ],
        },
    ],
    "productivity": [
        {
            "key": "barnamerizi", "name": "چله برنامه‌ریزی روزانه",
            "display_name": "برنامه‌ریزی و پیگیری روز",
            "task": "نوشتن برنامه شب قبل و بازبینی انجام‌ها در پایان روز",
            "levels": [
                {"title": "فقط نوشتن برنامه", "score": 1, "color": "#FFE082"},
                {"title": "نوشتن برنامه + بازبینی", "score": 3, "color": "#FFB300"},
                {"title": "برنامه + بازبینی + ۸۰٪ انجام", "score": 5, "color": "#FF8F00"},
            ],
        },
        {
            "key": "kar-amigh", "name": "چله کار عمیق",
            "display_name": "کار عمیق روزانه",
            "task": "روزی حداقل یک بلوک ۹۰ دقیقه‌ای تمرکز کامل بدون موبایل",
            "levels": [
                {"title": "۴۵ دقیقه تمرکز", "score": 1, "color": "#FFE082"},
                {"title": "۱ بلوک ۹۰ دقیقه‌ای", "score": 3, "color": "#FFB300"},
                {"title": "۲ بلوک ۹۰ دقیقه‌ای", "score": 5, "color": "#FF8F00"},
            ],
        },
    ],
    "family": [
        {
            "key": "mehrabani", "name": "چله مهربانی خانوادگی",
            "display_name": "رابطه بهتر با خانواده",
            "task": "روزی یک گفت‌وگوی صمیمی یا کار محبت‌آمیز برای خانواده",
            "levels": [
                {"title": "سلام و احوالپرسی صمیمانه", "score": 1, "color": "#F48FB1"},
                {"title": "گفت‌وگوی ۱۰ دقیقه‌ای", "score": 3, "color": "#EC407A"},
                {"title": "گفت‌وگو + کار محبت‌آمیز", "score": 5, "color": "#AD1457"},
            ],
        },
        {
            "key": "sele-raham", "name": "چله صله رحم",
            "display_name": "صله رحم روزانه",
            "task": "تماس یا دیدار با خویشاوندان و رسیدگی به پیوندها",
            "levels": [
                {"title": "پیام صمیمانه", "score": 1, "color": "#F48FB1"},
                {"title": "تماس صوتی", "score": 3, "color": "#EC407A"},
                {"title": "دیدار حضوری", "score": 5, "color": "#AD1457"},
            ],
        },
    ],
}


# ---------- ویجت «چله‌های آماده» ----------
def build_ready_section(app, on_pick) -> ft.Control:
    """on_pick(tpl) زمانی صدا زده می‌شود که کاربر یک قالب را انتخاب کند."""
    page = app.page

    state = {
        "type": READY_TYPES[0]["key"],  # پیش‌فرض: اولین نوع انتخاب باشد
        "selected": None,
    }

    counter = ft.Text("", size=11, color=ft.Colors.GREY_500)
    list_column = ft.Column(spacing=8)

    def type_icon(tkey: str):
        for t in READY_TYPES:
            if t["key"] == tkey:
                return t["icon"]
        return ft.Icons.STAR_OUTLINE

    def make_template_tile(tpl: dict, tkey: str) -> ft.Container:
        is_sel = state["selected"] == tpl["key"]
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(type_icon(tkey), size=20,
                                    color=ft.Colors.PRIMARY),
                    width=38, height=38,
                    bgcolor=ft.Colors.with_opacity(0.10, ft.Colors.PRIMARY),
                    border_radius=11,
                ),
                ft.Column([
                    ft.Text(tpl["name"], size=13, weight=ft.FontWeight.BOLD),
                    ft.Text(tpl.get("task", ""), size=11,
                            color=ft.Colors.GREY_600),
                    ft.Text(f"{len(tpl['levels'])} سطح", size=10,
                            color=ft.Colors.GREY_500),
                ], spacing=2, expand=True),
                (
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE, size=18,
                                color=ft.Colors.GREEN_600),
                        ft.Text("بارگذاری شد", size=11,
                                color=ft.Colors.GREEN_700,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=4)
                    if is_sel else
                    ft.TextButton(
                        "انتخاب",
                        icon=ft.Icons.DOWNLOAD_OUTLINED,
                        on_click=lambda e, tp=tpl: pick(tp),
                    )
                ),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.Padding.symmetric(horizontal=10, vertical=8),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY)
                    if is_sel else ft.Colors.SURFACE_CONTAINER_LOW,
            border_radius=14,
            border=ft.Border.all(
                1,
                ft.Colors.PRIMARY if is_sel
                else ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
            ),
            on_click=lambda e, tp=tpl: pick(tp),
        )

    def fill_list():
        tkey = state["type"]
        tpls = READY_TEMPLATES.get(tkey, [])
        list_column.controls = [make_template_tile(t, tkey) for t in tpls]
        counter.value = f"{len(tpls)} قالب آماده"

    def on_type_select(e):
        state["type"] = e.control.value   # value = key نوع انتخاب‌شده
        state["selected"] = None
        fill_list()
        page.update()

    def pick(tpl: dict):
        state["selected"] = tpl["key"]
        fill_list()
        page.update()
        on_pick(tpl)  # apply_template خودش refresh_levels و page.update را صدا می‌زند

    type_dd = ft.Dropdown(
        label="نوع چله",
        value=state["type"],
        filled=True,
        leading_icon=ft.Icons.CATEGORY,
        options=[
            ft.DropdownOption(key=t["key"], text=t["title"],
                              leading_icon=t["icon"])
            for t in READY_TYPES
        ],
        on_select=on_type_select,   # ← در فلت 1.0 روی Dropdown رویداد on_select است
    )

    fill_list()   # پر کردن اولیه؛ بدون page.update (کنترل‌ها هنوز به صفحه اضافه نشده‌اند)

    header = ft.Row([
        ft.Icon(ft.Icons.STARS, size=18, color=ft.Colors.PRIMARY),
        ft.Text("چله‌های آماده", size=14, weight=ft.FontWeight.BOLD),
        ft.Container(expand=True),
        counter,
    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    tip = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=ft.Colors.BLUE_700),
            ft.Text(
                "نوع چله را انتخاب کن، بعد یکی از قالب‌ها را بزن تا نام، "
                "وظیفه و سطوح آن در فرم پایین پر شود.",
                size=11, color=ft.Colors.GREY_600, expand=True),
        ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.START),
        padding=ft.Padding.symmetric(vertical=8, horizontal=10),
        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.BLUE),
        border_radius=10,
    )

    return elevated_card(
        ft.Column([header, tip, type_dd, list_column], spacing=12),
        padding=16,
    )