"""مدیریت ظاهر برنامه: تم روشن/تاریک، فونت، قالب رنگی و پس‌زمینه (رنگ/تصویر).

ذخیره‌سازی فایل‌ها طبق راهنمای رسمی فلت با متغیرهای محیطی
FLET_APP_STORAGE_DATA / FLET_APP_STORAGE_CACHE / FLET_APP_STORAGE_TEMP
انجام می‌شود (نه با expanduser("~") و نه با صفات page — که روی اندروید
منجر به PermissionError می‌شد).
"""

import os
import json
import shutil
import colorsys
import tempfile

import flet as ft
from PIL import Image


# ---------- گزینه‌های ظاهری ----------
FONT_CHOICES = [
    {"key": "",         "title": "پیش‌فرض",   "family": ""},
    {"key": "vazirmatn","title": "وزیرمتن",   "family": "Vazirmatn"},
    {"key": "sahel",    "title": "ساحل",      "family": "Sahel"},
    {"key": "shabnam",  "title": "شبنم",      "family": "Shabnam"},
    {"key": "estedad",  "title": "استعداد",   "family": "Estedad"},
    {"key": "tahoma",   "title": "Tahoma",    "family": "Tahoma"},
]

# برای هر پس‌زمینه، نسخهٔ روشن و تاریک جدا تعریف شده تا با تم هماهنگ بماند
BACKGROUNDS = [
    {"key": "default", "title": "پیش‌فرض",    "light": None,      "dark": None},
    {"key": "white",   "title": "سفید",      "light": "#FFFFFF", "dark": "#121212"},
    {"key": "cream",   "title": "کرم",       "light": "#FAF6EE", "dark": "#1C1A17"},
    {"key": "grey",    "title": "خاکستری",   "light": "#F1F3F5", "dark": "#17181A"},
    {"key": "mint",    "title": "سبز ملایم", "light": "#EDF7F0", "dark": "#122019"},
    {"key": "sky",     "title": "آبی ملایم", "light": "#EDF3FA", "dark": "#131A22"},
    {"key": "image",   "title": "تصویر",     "light": None,      "dark": None, "is_image": True},
]


# ---------- ابزار ترکیب رنگ ----------
def _mix(c1: str, c2: str, t: float) -> str:
    """ترکیب خطی دو رنگ hex؛ t=0 → c1 و t=1 → c2"""
    c1, c2 = c1.lstrip("#"), c2.lstrip("#")
    r1, g1, b1 = int(c1[0:2], 16), int(c1[2:4], 16), int(c1[4:6], 16)
    r2, g2, b2 = int(c2[0:2], 16), int(c2[2:4], 16), int(c2[4:6], 16)
    return "#{:02X}{:02X}{:02X}".format(
        round(r1 + (r2 - r1) * t),
        round(g1 + (g2 - g1) * t),
        round(b1 + (b2 - b1) * t),
    )


# ---------- پالت‌های استاندارد Material (hex صریح) ----------
HUE_SHADES = {
    "GREEN": {
        50: "#E8F5E9", 100: "#C8E6C9", 200: "#A5D6A7", 300: "#81C784",
        400: "#66BB6A", 500: "#4CAF50", 600: "#43A047", 700: "#388E3C",
        800: "#2E7D32", 900: "#1B5E20",
    },
    "TEAL": {
        50: "#E0F2F1", 100: "#B2DFDB", 200: "#80CBC4", 300: "#4DB6AC",
        400: "#26A69A", 500: "#009688", 600: "#00897B", 700: "#00796B",
        800: "#00695C", 900: "#004D40",
    },
    "BLUE": {
        50: "#E3F2FD", 100: "#BBDEFB", 200: "#90CAF9", 300: "#64B5F6",
        400: "#42A5F5", 500: "#2196F3", 600: "#1E88E5", 700: "#1976D2",
        800: "#1565C0", 900: "#0D47A1",
    },
    "INDIGO": {
        50: "#E8EAF6", 100: "#C5CAE9", 200: "#9FA8DA", 300: "#7986CB",
        400: "#5C6BC0", 500: "#3F51B5", 600: "#3949AB", 700: "#303F9F",
        800: "#283593", 900: "#1A237E",
    },
    "PURPLE": {
        50: "#F3E5F5", 100: "#E1BEE7", 200: "#CE93D8", 300: "#BA68C8",
        400: "#AB47BC", 500: "#9C27B0", 600: "#8E24AA", 700: "#7B1FA2",
        800: "#6A1B9A", 900: "#4A148C",
    },
    "ORANGE": {
        50: "#FFF3E0", 100: "#FFE0B2", 200: "#FFCC80", 300: "#FFB74D",
        400: "#FFA726", 500: "#FF9800", 600: "#FB8C00", 700: "#F57C00",
        800: "#EF6C00", 900: "#E65100",
    },
}

COLOR_SCHEMES = [
    {"key": "green",  "title": "سبز",       "base": "GREEN",  "swatch": "#43A047"},
    {"key": "teal",   "title": "فیروزه‌ای", "base": "TEAL",   "swatch": "#00897B"},
    {"key": "blue",   "title": "آبی",       "base": "BLUE",   "swatch": "#1E88E5"},
    {"key": "indigo", "title": "نیلی",      "base": "INDIGO", "swatch": "#3949AB"},
    {"key": "purple", "title": "بنفش",      "base": "PURPLE", "swatch": "#8E24AA"},
    {"key": "orange", "title": "نارنجی",    "base": "ORANGE", "swatch": "#FB8C00"},
    {"key": "custom", "title": "از تصویر",  "base": None,     "swatch": "#607D8B"},
]


def _lum(hexc: str) -> float:
    """روشنایی نسبی WCAG"""
    c = hexc.lstrip("#")
    def f(u):
        u /= 255
        return u / 12.92 if u <= 0.03928 else ((u + 0.055) / 1.055) ** 2.4
    r, g, b = f(int(c[0:2], 16)), f(int(c[2:4], 16)), f(int(c[4:6], 16))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def pick_text_on(bg: str) -> str:
    """متن سیاه یا سفید روی این پس‌زمینه خواناتر است؟"""
    def contrast(a, b):
        la, lb = _lum(a), _lum(b)
        return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
    return "#000000" if contrast(bg, "#000000") >= contrast(bg, "#FFFFFF") else "#FFFFFF"


# ---------- استخراج پالت رنگ از تصویر ----------
def extract_palette(image_path: str, n: int = 6):
    """رنگ‌های غالب تصویر، مرتب بر اساس «زنده‌بودن»"""
    img = Image.open(image_path).convert("RGB")
    img.thumbnail((160, 160))
    method = getattr(Image, "Quantize", Image).MEDIANCUT
    q = img.quantize(colors=n, method=method)

    total = img.width * img.height
    counts = sorted(q.getcolors(total), reverse=True)
    pal = q.getpalette()

    scored = []
    for cnt, idx in counts[:n]:
        r, g, b = pal[idx * 3: idx * 3 + 3]
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        hexc = "#{:02X}{:02X}{:02X}".format(r, g, b)
        score = s * (1 - abs(l - 0.5)) * (0.5 + 0.5 * cnt / total)
        scored.append((round(score, 4), hexc))
    return sorted(scored, reverse=True)


# ---------- ساخت طیف 50..900 از یک رنگ پایه ----------
def shades_from(base_hex: str) -> dict:
    """هم‌ساختارِ HUE_SHADES — قابل استفاده مستقیم در _build_color_scheme"""
    base = base_hex.lstrip("#")
    W, B = "#FFFFFF", "#000000"
    return {
        50:  _mix(W, base, 0.06),   100: _mix(W, base, 0.15),
        200: _mix(W, base, 0.30),   300: _mix(W, base, 0.50),
        400: _mix(W, base, 0.72),   500: "#" + base,
        600: _mix(base, B, 0.12),   700: _mix(base, B, 0.26),
        800: _mix(base, B, 0.42),   900: _mix(base, B, 0.58),
    }


class ThemeMixin:
    """مدیریت حالت شب/روز، ظاهر و پس‌زمینهٔ تصویری"""

    def apply_theme(self):
        """اعمال حالت شب روی page"""
        mapping = {
            "light": ft.ThemeMode.LIGHT,
            "dark": ft.ThemeMode.DARK,
            "system": ft.ThemeMode.SYSTEM,
        }
        self.page.theme_mode = mapping.get(self.theme_mode, ft.ThemeMode.LIGHT)
        self.apply_appearance()
        self.page.update()

    async def toggle_theme(self):
        """تغییر بین حالت روشن و تاریک"""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.db.set_setting("theme_mode", self.theme_mode)
        self.apply_theme()
        self.refresh()

    def _build_color_scheme(self, H: dict, dark: bool, bg_hex):
        """پالت کامل برای یک طیف شیدی (dict با کلیدهای 50..900)"""
        if not dark:
            surface = _mix(bg_hex, H[100], 0.25) if bg_hex \
                else _mix("#FFFFFF", H[100], 0.20)
            return ft.ColorScheme(
                primary=H[600],
                on_primary=pick_text_on(H[600]),
                primary_container=H[100],
                on_primary_container=H[900],
                secondary=H[700],
                on_secondary=pick_text_on(H[700]),
                secondary_container=H[50],
                on_secondary_container=H[900],
                surface=surface,
                on_surface="#1C1B1F",
                on_surface_variant="#49454F",
                surface_container_lowest=_mix(surface, "#FFFFFF", 0.60),
                surface_container_low=_mix(surface, "#000000", 0.03),
                surface_container=_mix(surface, "#000000", 0.06),
                surface_container_high=_mix(surface, "#000000", 0.09),
                surface_container_highest=_mix(surface, "#000000", 0.12),
                outline="#79747E",
                outline_variant=_mix(surface, "#000000", 0.15),
            )

        surface = _mix(bg_hex, H[900], 0.35) if bg_hex \
            else _mix("#141218", H[900], 0.35)
        return ft.ColorScheme(
            primary=H[300],
            on_primary=pick_text_on(H[300]),
            primary_container=H[900],
            on_primary_container=H[100],
            secondary=H[300],
            on_secondary=pick_text_on(H[300]),
            secondary_container=H[800],
            on_secondary_container=H[100],
            surface=surface,
            on_surface="#E6E1E5",
            on_surface_variant="#CAC4D0",
            surface_container_lowest=_mix(surface, "#000000", 0.30),
            surface_container_low=_mix(surface, "#FFFFFF", 0.05),
            surface_container=_mix(surface, "#FFFFFF", 0.08),
            surface_container_high=_mix(surface, "#FFFFFF", 0.11),
            surface_container_highest=_mix(surface, "#FFFFFF", 0.14),
            outline="#938F99",
            outline_variant=_mix(surface, "#FFFFFF", 0.12),
        )

    def apply_appearance(self):
        """اعمال فونت، قالب رنگی و پس‌زمینه از روی تنظیمات ذخیره‌شده.

        توجه: تصویر پس‌زمینه اینجا اعمال نمی‌شود — در API جدید
        page.decoration بی‌اثر است؛ تصویر توسط bg_image() روی
        کانتینر ریشهٔ هر View (در router) اعمال می‌شود.
        """
        page = self.page

        # قالب رنگی
        scheme_key = self.db.get_setting("color_scheme", "green")
        scheme = next((s for s in COLOR_SCHEMES if s["key"] == scheme_key),
                      COLOR_SCHEMES[0])

        # پس‌زمینه
        bg_key = self.db.get_setting("background", "default")
        bg = next((b for b in BACKGROUNDS if b["key"] == bg_key), BACKGROUNDS[0])

        is_dark = self.theme_mode == "dark"
        if self.theme_mode == "system":
            try:
                is_dark = page.platform_brightness == ft.Brightness.DARK
            except Exception:
                is_dark = False

        # فونت
        font_key = self.db.get_setting("font_family", "")
        family = next(
            (f["family"] for f in FONT_CHOICES if f["key"] == font_key), ""
        ) or None

        # طیف شیدی: استاندارد یا استخراج‌شده از تصویر
        if scheme["base"]:
            shades = HUE_SHADES[scheme["base"]]
        else:
            shades = shades_from(self._load_img_palette()[0])

        cs_light = self._build_color_scheme(shades, False, bg["light"])
        cs_dark = self._build_color_scheme(shades, True, bg["dark"])

        page.theme = ft.Theme(font_family=family, color_scheme=cs_light)
        page.dark_theme = ft.Theme(font_family=family, color_scheme=cs_dark)

        img_path = (self.db.get_setting("bg_image", "") or "") if bg_key == "image" else ""
        if img_path and os.path.exists(img_path):
            page.bgcolor = _mix(min(self._load_img_palette(), key=_lum), "#000000", 0.2)
        else:
            page.bgcolor = bg["dark"] if is_dark else bg["light"]

        page.update()

    # ------------------------------------------------------------------
    # تصویر پس‌زمینه (API جدید: Container.image روی ریشهٔ هر View)
    # ------------------------------------------------------------------

    def bg_image(self):
        """ft.DecorationImage | None — توسط router روی کانتینر ریشهٔ هر view
        به‌صورت image=self.bg_image() استفاده می‌شود.

        فایل همیشه داخل sandbox خود اپ ذخیره می‌شود
        (FLET_APP_STORAGE_DATA)؛ بنابراین Flutter روی اندروید هم
        بدون مشکل می‌تواند آن را بخواند.
        """
        if self.db.get_setting("background", "default") == "image":
            p = self.db.get_setting("bg_image", "") or ""
            if p and os.path.exists(p):
                return ft.DecorationImage(src=p, fit=ft.BoxFit.COVER)
        return None

    def image_scrim(self):
        """لایهٔ نیمه‌شفاف برای خوانایی متن روی تصویر (اختیاری)"""
        is_dark = self.theme_mode == "dark"
        return ft.Container(
            expand=True,
            bgcolor=ft.Colors.with_opacity(
                0.60 if is_dark else 0.55,
                ft.Colors.BLACK if is_dark else ft.Colors.WHITE,
            ),
        )

    def clear_background_image(self, e=None):
        """حذف تصویر پس‌زمینه و بازگشت به پس‌زمینهٔ پیش‌فرض"""
        # پاک‌کردن فایل‌های ذخیره‌شده (به‌ازای هر پسوند ممکن)
        dst_dir = os.path.join(self._bg_storage_dir(), "backgrounds")
        if os.path.isdir(dst_dir):
            for f in os.listdir(dst_dir):
                if f.startswith("bg."):
                    try:
                        os.remove(os.path.join(dst_dir, f))
                    except OSError:
                        pass

        self.db.set_setting("bg_image", "")
        self.db.set_setting("img_palette", "[]")
        self.db.set_setting("background", "default")

        self.apply_appearance()
        cb = getattr(self, "_on_bg_changed", None)
        if cb:
            cb()
        self.refresh()

    # ------------------------------------------------------------------
    # FilePicker (API جدید: سرویس — نه کنترل ویژوال)
    # ------------------------------------------------------------------

    def setup_bg_picker(self):
        if getattr(self, "_bg_picker", None) is not None:
            return
        self._bg_picker = ft.FilePicker()
        if hasattr(self.page, "services"):
            self.page.services.append(self._bg_picker)
        # ⚠️ هرگز page.overlay.append نکنید → باکس قرمز

    async def pick_background_image(self, e=None):
        self.setup_bg_picker()
        try:
            files = await self._bg_picker.pick_files(
                dialog_title="انتخاب تصویر پس‌زمینه",
                allow_multiple=False,
                # روی اندروید انتخاب‌گر تصویر سیستم (گالری) باز می‌شود؛
                # مطمئن‌تر و با UX بهتر از CUSTOM + allowed_extensions
                file_type=ft.FilePickerFileType.IMAGE,
            )
        except Exception as ex:
            self.snack(f"خطا در باز کردن دیالوگ: {ex}")
            return
        if files:
            # ⚠️ فایل پیک‌شده در location موقتی است و ممکن است با پایان
            # session پاک شود → بلافاصله کپی می‌کنیم (توصیهٔ مستندات فلت)
            self._register_picked_image(files[0].path)

    # ------------------------------------------------------------------
    # محل ذخیره‌سازی فایل‌ها — طبق راهنمای رسمی فلت
    # ------------------------------------------------------------------

    def _bg_storage_dir(self) -> str:
        """مسیر مطلق و دائمی برای نگهداری تصاویر پس‌زمینه.

        فلت در همهٔ پلتفرم‌ها این متغیرهای محیطی را ست می‌کند:
          FLET_APP_STORAGE_DATA  → دادهٔ دائمی؛ OS هرگز پاکش نمی‌کند،
                                   با آپدیت اپ حفظ می‌شود، و همچنین
                                   working directory برنامه است.
          FLET_APP_STORAGE_CACHE → کشِ قابل بازیابی؛ OS ممکن است پاکش کند.
          FLET_APP_STORAGE_TEMP  → موقت؛ ممکن است بین دو اجرا حذف شود.

        برای تصویری که کاربر انتخاب کرده و باید بماند، DATA درست‌ترین
        انتخاب است. (expanduser("~") روی اندروید HOME=/data می‌دهد
        که نوشتنی نیست و باعث PermissionError می‌شد.)
        """
        data = os.getenv("FLET_APP_STORAGE_DATA")
        if data and os.path.isdir(data):
            return data

        # fallback — فقط وقتی خارج از runtime فلت اجرا شود (تست/ابزار)
        for cand in (
            os.getenv("FLET_APP_STORAGE_CACHE"),
            os.getenv("TMPDIR"),
            tempfile.gettempdir(),
        ):
            if cand and os.path.isdir(cand):
                return cand
        return os.getcwd()

    def _load_img_palette(self) -> list:
        try:
            pal = json.loads(self.db.get_setting("img_palette", "[]"))
            pal = [h for h in pal if isinstance(h, str) and h.startswith("#")]
        except Exception:
            pal = []
        return pal or ["#607D8B"]

    def _register_picked_image(self, src_path: str):
        """کپی به محل دائمی + استخراج پالت + اعمال"""
        try:
            dst_dir = os.path.join(self._bg_storage_dir(), "backgrounds")
            os.makedirs(dst_dir, exist_ok=True)

            ext = os.path.splitext(src_path)[1].lower() or ".png"
            dst = os.path.join(dst_dir, f"bg{ext}")
            shutil.copy(src_path, dst)

            # فایل باقی‌مانده از انتخاب قبلی با پسوند دیگر را پاک کن
            for f in os.listdir(dst_dir):
                if f.startswith("bg.") and f != os.path.basename(dst):
                    try:
                        os.remove(os.path.join(dst_dir, f))
                    except OSError:
                        pass
        except Exception as ex:
            self.snack(f"ذخیرهٔ تصویر ممکن نشد: {ex}")
            return

        self.db.set_setting("bg_image", dst)
        self.db.set_setting("img_palette", json.dumps([h for _, h in extract_palette(dst)]))
        self.db.set_setting("background", "image")

        self.apply_appearance()
        cb = getattr(self, "_on_bg_changed", None)
        if cb:
            cb()
        self.refresh()
        self.snack("تصویر پس‌زمینه اعمال شد ✅")