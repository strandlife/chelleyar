from __future__ import annotations
from datetime import time as dtime, timedelta

import flet as ft
import jdatetime

__all__ = ["ShamsiCalendar", "ShamsiDateEdit", "ShamsiTimeEdit", "ShamsiDateTimeEdit",
           "format_jdate", "format_time", "parse_jdate", "parse_time",
           "open_date_dialog"]

# ───────────────────────── ثابت‌ها و ابزارها ─────────────────────────

J_MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
J_WEEKDAYS = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]
J_WEEKDAYS_SHORT = ["ش", "ی", "د", "س", "چ", "پ", "ج"]

_FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_EN = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

def fa(s): return str(s).translate(_FA)
def en(s): return str(s).translate(_EN)

def _days_in_month(jy, jm):
    if jm <= 6:  return 31
    if jm <= 11: return 30
    return 30 if jdatetime.date(jy, 1, 1).isleap() else 29

def _clamp_date(d, mn, mx):
    if mn and d < mn: return mn
    if mx and d > mx: return mx
    return d

def _clamp_datetime(dt, mn, mx):
    if mn and dt < mn: return mn
    if mx and dt > mx: return mx
    return dt

def _as_datetime(x):
    if isinstance(x, jdatetime.datetime): return x
    if isinstance(x, jdatetime.date): return jdatetime.datetime(x.year, x.month, x.day)
    return x

def _shift_date(d, days):
    g = d.togregorian() + timedelta(days=days)
    return jdatetime.date.fromgregorian(date=g)

# ---------- اندازه‌ها: دو حالت دسکتاپ / موبایل ----------

S_DESKTOP = dict(
    day_h=36, wd_h=22, fs_day=14, fs_wd=13,
    icon=40, spin_w=34, spin_h=20,
    m_w=110, y_w=90, m_expand=None, y_expand=None,      # دسکتاپ: عرض ثابت
    f_y=60, f_m=52, f_d=52, f_h=48, f_expand=None,
    fs_field=14, fs_sep=15, gap=4,
)
S_MOBILE = dict(
    day_h=32, wd_h=20, fs_day=12, fs_wd=11,
    icon=30, spin_w=28, spin_h=18,
    m_w=None, y_w=None, m_expand=3, y_expand=2,          # موبایل: فلکس ۳ به ۲
    f_y=None, f_m=None, f_d=None, f_h=None, f_expand=2,  # فیلدهای تاریخ/ساعت هم فلکس
    fs_field=13, fs_sep=13, gap=3,
)

def _is_mobile(page) -> bool:
    """تشخیص موبایل — هم enum جدید (ft.PagePlatform) و هم رشتهٔ قدیمی"""
    try:
        p = getattr(page, "platform", "")
        name = getattr(p, "name", str(p))
        return str(name).lower() in ("android", "ios")
    except Exception:
        return False

def _spin_widget(S, on_up, on_down):
    """دکمه‌های بالا/پایین مشترک بین DateEdit و TimeEdit"""
    up = ft.IconButton(ft.Icons.ARROW_DROP_UP, width=S["spin_w"], height=S["spin_h"],
                       style=ft.ButtonStyle(padding=0),
                       tooltip="زیاد کردن بخش انتخاب‌شده", on_click=on_up)
    dn = ft.IconButton(ft.Icons.ARROW_DROP_DOWN, width=S["spin_w"], height=S["spin_h"],
                       style=ft.ButtonStyle(padding=0),
                       tooltip="کم کردن بخش انتخاب‌شده", on_click=on_down)
    return ft.Column([up, dn], spacing=0), up, dn

def _cal_dialog(page, title, content, actions):
    """AlertDialog با padding فشرده روی موبایل (پیش‌فرض فلت ۴۰px حاشیه می‌گذارد)"""
    mob = _is_mobile(page)
    return ft.AlertDialog(
        modal=True,
        title=ft.Text(title, size=16 if mob else 18),
        title_padding=ft.Padding.only(left=16, right=16, top=16 if mob else 24),
        content=content,
        content_padding=ft.Padding.all(10 if mob else 24),
        inset_padding=ft.Padding.symmetric(horizontal=16, vertical=24) if mob
                      else ft.Padding.symmetric(horizontal=40, vertical=24),
        actions=actions,
    )

# ---------- ابزار تاریخ/زمان ----------

def format_jdate(d, fmt="yyyy/MM/dd", persian=True):
    out, i = [], 0
    while i < len(fmt):
        for tok in ("WWWW", "MMMM", "yyyy", "yy", "MM", "dd", "M", "d"):
            if fmt.startswith(tok, i):
                if   tok == "WWWW": out.append(J_WEEKDAYS[d.weekday()])
                elif tok == "MMMM": out.append(J_MONTHS[d.month - 1])
                elif tok == "yyyy": out.append(str(d.year))
                elif tok == "yy":   out.append(f"{d.year % 100:02d}")
                elif tok == "MM":   out.append(f"{d.month:02d}")
                elif tok == "dd":   out.append(f"{d.day:02d}")
                elif tok == "M":    out.append(str(d.month))
                else:               out.append(str(d.day))
                i += len(tok)
                break
        else:
            out.append(fmt[i]); i += 1
    return fa("".join(out)) if persian else "".join(out)

def format_time(t, fmt="HH:MM", persian=True):
    out, i = [], 0
    while i < len(fmt):
        for tok in ("HH", "MM", "SS", "H", "M", "S"):
            if fmt.startswith(tok, i):
                if   tok == "HH": out.append(f"{t.hour:02d}")
                elif tok == "MM": out.append(f"{t.minute:02d}")
                elif tok == "SS": out.append(f"{t.second:02d}")
                elif tok == "H":  out.append(str(t.hour))
                elif tok == "M":  out.append(str(t.minute))
                else:             out.append(str(t.second))
                i += len(tok)
                break
        else:
            out.append(fmt[i]); i += 1
    return fa("".join(out)) if persian else "".join(out)

def parse_jdate(s):
    try:
        y, m, d = [int(x) for x in en(s).replace("-", "/").split("/")]
        return jdatetime.date(y, m, d)
    except Exception:
        return None

def parse_time(s):
    try:
        p = [int(x) for x in en(s).split(":")]
        while len(p) < 3: p.append(0)
        return dtime(*p[:3])
    except Exception:
        return None

def show_dialog(page, dlg):
    (page.show_dialog(dlg) if hasattr(page, "show_dialog") else page.open(dlg))

def close_dialog(page, dlg):
    (page.pop_dialog() if hasattr(page, "pop_dialog") else page.close(dlg))

# ───────────────────── ۱) ShamsiCalendar ─────────────────────

class ShamsiCalendar:
    """تقویم شمسی — سلول‌ها واکنش‌گرا هستند (expand) و همیشه در عرض دیالوگ جا می‌شوند.
    compact=None → خودکار بر اساس پلتفرم (True/False برای اجبار)"""

    def __init__(self, on_change=None, value=None, min_date=None, max_date=None,
                 first_year=1300, last_year=1500, show_today_button=True, compact=None):
        self.on_change = on_change
        self._min, self._max = min_date, max_date
        self.first_year, self.last_year = first_year, last_year
        self.show_today_button = show_today_button
        self.compact = compact
        self.value = _clamp_date(value or jdatetime.date.today(), min_date, max_date)
        self._vy, self._vm = self.value.year, self.value.month
        self._page_obj = None
        self.body = ft.Column(spacing=4, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)
        self._render()

    # — property _page: با ست‌کردن صفحه، اندازه‌ها طبق پلتفرم دوباره اعمال می‌شود —
    @property
    def _page(self): return self._page_obj

    @_page.setter
    def _page(self, p):
        self._page_obj = p
        self._render()

    def _S(self):
        if self.compact is not None:
            return S_MOBILE if self.compact else S_DESKTOP
        return S_MOBILE if _is_mobile(self._page_obj) else S_DESKTOP

    # — API —
    def selected_date(self): return self.value

    def set_date(self, d):
        d = _clamp_date(d, self._min, self._max)
        changed = d != self.value
        self.value = d
        self._vy, self._vm = d.year, d.month
        self._page_update()
        if changed and self.on_change: self.on_change(self.value)

    def set_date_range(self, mn=None, mx=None):
        self._min, self._max = mn, mx
        self.value = _clamp_date(self.value, mn, mx)
        self._vy, self._vm = self.value.year, self.value.month
        self._page_update()

    def show_today(self): self.set_date(jdatetime.date.today())
    def next_month(self): self._nav(+1)
    def previous_month(self): self._nav(-1)

    # — داخلی —
    def _page_update(self):
        self._render()
        if self._page_obj: self._page_obj.update()

    def _nav(self, delta):
        m, y = self._vm + delta, self._vy
        if m == 0:    m, y = 12, y - 1
        elif m == 13: m, y = 1, y + 1
        self._vy, self._vm = y, m
        self._page_update()

    def _view(self, m, y):
        self._vm, self._vy = m, y
        self._page_update()

    def _render(self):
        controls = [self._header(), self._weekdays(), self._grid()]
        if self.show_today_button:
            controls.append(self._today_row())
        self.body.controls = controls

    def _header(self):
        S = self._S()
        y_lo, y_hi = min(self.first_year, self._vy), max(self.last_year, self._vy)
        return ft.Row([
            ft.IconButton(ft.Icons.CHEVRON_LEFT, tooltip="ماه قبل",
                          width=S["icon"], height=S["icon"],
                          style=ft.ButtonStyle(padding=0),
                          on_click=lambda e: self._nav(-1)),
            # expand → عرض ثابت نیست؛ سهمی از فضای موجود می‌گیرد و جمع می‌شود
            ft.Dropdown(width=S["m_w"], expand=S["m_expand"], value=str(self._vm),
                        options=[ft.DropdownOption(key=str(m), text=J_MONTHS[m - 1])
                                 for m in range(1, 13)],
                        on_select=lambda e: self._view(int(e.control.value), self._vy)),
            ft.Dropdown(width=S["y_w"], expand=S["y_expand"], value=str(self._vy),
                        options=[ft.DropdownOption(key=str(y), text=fa(y))
                                 for y in range(y_lo, y_hi + 1)],
                        on_select=lambda e: self._view(self._vm, int(e.control.value))),
            ft.IconButton(ft.Icons.CHEVRON_RIGHT, tooltip="ماه بعد",
                          width=S["icon"], height=S["icon"],
                          style=ft.ButtonStyle(padding=0),
                          on_click=lambda e: self._nav(+1)),
        ], spacing=S["gap"],
           alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
           vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _weekdays(self):
        S = self._S()
        return ft.Row(
            [ft.Container(ft.Text(w, size=S["fs_wd"], weight=ft.FontWeight.BOLD,
                                  text_align=ft.TextAlign.CENTER),
                          expand=True, height=S["wd_h"], alignment=ft.Alignment.CENTER)
             for w in reversed(J_WEEKDAYS_SHORT)],
            spacing=2)

    def _grid(self):
        S = self._S()
        offset = jdatetime.date(self._vy, self._vm, 1).weekday()   # شنبه = ۰
        spacer = lambda: ft.Container(expand=True, height=S["day_h"])
        cells = [spacer() for _ in range(offset)]
        cells += [self._day_cell(d) for d in range(1, _days_in_month(self._vy, self._vm) + 1)]
        rows = [cells[i:i + 7] for i in range(0, len(cells), 7)]
        rows[-1] += [spacer() for _ in range(7 - len(rows[-1]))]
        return ft.Column([ft.Row(r[::-1], spacing=2) for r in rows],
                         spacing=2, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def _day_cell(self, day):
        S = self._S()
        d = jdatetime.date(self._vy, self._vm, day)
        disabled = (self._min and d < self._min) or (self._max and d > self._max)
        selected = (d == self.value)
        today = (d == jdatetime.date.today())
        if selected:
            st = ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY, color=ft.Colors.ON_PRIMARY, padding=0)
        elif today:
            st = ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY_CONTAINER,
                                color=ft.Colors.ON_PRIMARY_CONTAINER, padding=0)
        else:
            st = ft.ButtonStyle(padding=0)
        return ft.TextButton(
            content=ft.Text(fa(day), size=S["fs_day"],
                            weight=ft.FontWeight.BOLD if (selected or today) else ft.FontWeight.NORMAL),
            expand=True, height=S["day_h"], style=st, disabled=disabled,
            on_click=lambda e, dd=day: self.set_date(jdatetime.date(self._vy, self._vm, dd)))

    def _today_row(self):
        S = self._S()
        return ft.Row([ft.TextButton("امروز", height=S["day_h"],
                                     on_click=lambda e: self.show_today())],
                      alignment=ft.MainAxisAlignment.END)


# ───────────────────── ۲) ShamsiDateEdit ─────────────────────

class ShamsiDateEdit:
    def __init__(self, on_change=None, value=None, min_date=None, max_date=None,
                 first_year=1300, last_year=1500, calendar_popup=True, compact=None):
        self.on_change = on_change
        self._min, self._max = min_date, max_date
        self.first_year, self.last_year = first_year, last_year
        self._section = "day"
        self._dlg = None
        self.compact = compact
        self._page_obj = None
        self.value = _clamp_date(value or jdatetime.date.today(), min_date, max_date)

        self.f_y = self._make_field("year")
        self.f_m = self._make_field("month")
        self.f_d = self._make_field("day")
        self._seps = [ft.Text("/", size=15, weight=ft.FontWeight.BOLD),
                      ft.Text("/", size=15, weight=ft.FontWeight.BOLD)]
        self._spin_col, up, dn = _spin_widget(self._S(),
                                              lambda e: self._step_section(+1),
                                              lambda e: self._step_section(-1))
        self._spin_btns = [up, dn]
        self._cal_btn = ft.IconButton(ft.Icons.CALENDAR_MONTH, tooltip="تقویم",
                                      width=self._S()["icon"], height=self._S()["icon"],
                                      style=ft.ButtonStyle(padding=0), on_click=self.open_popup)
        parts = [self.f_y, self._seps[0], self.f_m, self._seps[1], self.f_d,
                 self._spin_col, self._cal_btn]
        self.body = ft.Row(parts, spacing=3, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self._refresh()
        self._apply_sizes()

    # — property _page: اولین بار که صفحه ست شد، ابعاد موبایل/دسکتاپ اعمال می‌شود —
    @property
    def _page(self): return self._page_obj

    @_page.setter
    def _page(self, p):
        self._page_obj = p
        self._apply_sizes()

    def _S(self):
        if self.compact is not None:
            return S_MOBILE if self.compact else S_DESKTOP
        return S_MOBILE if _is_mobile(self._page_obj) else S_DESKTOP

    def _apply_sizes(self):
        S = self._S()
        for f, w in ((self.f_y, S["f_y"]), (self.f_m, S["f_m"]), (self.f_d, S["f_d"])):
            f.width, f.expand, f.text_size = w, S["f_expand"], S["fs_field"]
        for t in self._seps: t.size = S["fs_sep"]
        for b in self._spin_btns: b.width, b.height = S["spin_w"], S["spin_h"]
        self._cal_btn.width, self._cal_btn.height = S["icon"], S["icon"]

    def _make_field(self, sec):
        return ft.TextField(value="", width=60, dense=True, text_align=ft.TextAlign.CENTER,
                            on_focus=lambda e, s=sec: self._set_section(s),
                            on_blur=self._apply_all, on_submit=self._apply_all)

    def _set_section(self, sec): self._section = sec

    def _refresh(self):
        self.f_y.value = fa(self.value.year)
        self.f_m.value = fa(self.value.month)
        self.f_d.value = fa(self.value.day)

    def _apply_all(self, e=None):
        try:
            y = int(en(self.f_y.value)); m = int(en(self.f_m.value)); d = int(en(self.f_d.value))
        except ValueError:
            self._refresh(); self._page_update(); return
        y = min(max(y, self.first_year), self.last_year)
        m = min(max(m, 1), 12)
        d = min(max(d, 1), _days_in_month(y, m))
        self.set_date(jdatetime.date(y, m, d))

    # — API —
    def date(self): return self.value

    def set_date(self, d):
        d = _clamp_date(d, self._min, self._max)
        changed = d != self.value
        self.value = d
        self._refresh()
        self._page_update()
        if changed and self.on_change: self.on_change(self.value)

    def set_date_range(self, mn=None, mx=None):
        self._min, self._max = mn, mx
        self.set_date(self.value)

    def _page_update(self):
        if self._page_obj: self._page_obj.update()

    def _step_section(self, delta):
        y, m, d = self.value.year, self.value.month, self.value.day
        if self._section == "year":
            y = min(max(y + delta, self.first_year), self.last_year)
            d = min(d, _days_in_month(y, m))
        elif self._section == "month":
            m += delta
            if m == 0:    m, y = 12, y - 1
            elif m == 13: m, y = 1, y + 1
            d = min(d, _days_in_month(y, m))
        else:
            nd = _shift_date(jdatetime.date(y, m, d), delta)
            y, m, d = nd.year, nd.month, nd.day
        self.set_date(jdatetime.date(y, m, d))

    def open_popup(self, e=None):
        cal = ShamsiCalendar(on_change=self._picked, value=self.value,
                             min_date=self._min, max_date=self._max, compact=self.compact)
        cal._page = self._page   # رندر با اندازهٔ درست پلتفرم
        self._dlg = _cal_dialog(self._page, "انتخاب تاریخ", cal.body,
                                [ft.TextButton("بستن", on_click=self.close_popup)])
        show_dialog(self._page, self._dlg)

    def close_popup(self, e=None): close_dialog(self._page, self._dlg)

    def _picked(self, d):
        self.close_popup()
        self.set_date(d)


# ───────────────────── ۳) ShamsiTimeEdit ─────────────────────

class ShamsiTimeEdit:
    def __init__(self, on_change=None, value=None, minute_step=1, compact=None):
        self.on_change = on_change
        self._step_min = minute_step
        self._section = "minute"
        self.compact = compact
        self._page_obj = None
        self.value = value or dtime(0, 0)

        self.f_h = self._make_field("hour")
        self.f_m = self._make_field("minute")
        self._colon = ft.Text(":", size=15, weight=ft.FontWeight.BOLD)
        self._spin_col, up, dn = _spin_widget(self._S(),
                                              lambda e: self._step_section(+1),
                                              lambda e: self._step_section(-1))
        self._spin_btns = [up, dn]
        parts = [self.f_h, self._colon, self.f_m, self._spin_col]
        self.body = ft.Row(parts, spacing=3, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self._refresh()
        self._apply_sizes()

    @property
    def _page(self): return self._page_obj

    @_page.setter
    def _page(self, p):
        self._page_obj = p
        self._apply_sizes()

    def _S(self):
        if self.compact is not None:
            return S_MOBILE if self.compact else S_DESKTOP
        return S_MOBILE if _is_mobile(self._page_obj) else S_DESKTOP

    def _apply_sizes(self):
        S = self._S()
        for f, w in ((self.f_h, S["f_h"]), (self.f_m, S["f_m"])):
            f.width, f.expand, f.text_size = w, S["f_expand"], S["fs_field"]
        self._colon.size = S["fs_sep"]
        for b in self._spin_btns: b.width, b.height = S["spin_w"], S["spin_h"]

    def _make_field(self, sec):
        return ft.TextField(value="", width=48, dense=True, text_align=ft.TextAlign.CENTER,
                            on_focus=lambda e, s=sec: self._set_section(s),
                            on_blur=self._apply_all, on_submit=self._apply_all)

    def _set_section(self, sec): self._section = sec

    def _refresh(self):
        self.f_h.value = fa(self.value.hour)
        self.f_m.value = fa(self.value.minute)

    def _apply_all(self, e=None):
        try:
            h = int(en(self.f_h.value)); mi = int(en(self.f_m.value))
        except ValueError:
            self._refresh(); self._page_update(); return
        self.set_time(dtime(h % 24, mi % 60))

    # — API —
    def time(self): return self.value

    def set_time(self, t):
        changed = t != self.value
        self.value = t
        self._refresh()
        self._page_update()
        if changed and self.on_change: self.on_change(self.value)

    def _page_update(self):
        if self._page_obj: self._page_obj.update()

    def _step_section(self, delta):
        h, mi = self.value.hour, self.value.minute
        if self._section == "hour":
            h = (h + delta) % 24
        else:
            mi = (mi + delta * self._step_min) % 60
        self.set_time(dtime(h, mi))


# ───────────────────── ۴) ShamsiDateTimeEdit ─────────────────────

class ShamsiDateTimeEdit:
    def __init__(self, on_change=None, value=None, min_datetime=None, max_datetime=None,
                 calendar_popup=True, minute_step=1, first_year=1300, last_year=1500,
                 compact=None):
        self.on_change = on_change
        self._min = _as_datetime(min_datetime)
        self._max = _as_datetime(max_datetime)
        v = _clamp_datetime(_as_datetime(value) or jdatetime.datetime.today(), self._min, self._max)
        min_d = jdatetime.date(self._min.year, self._min.month, self._min.day) if self._min else None
        max_d = jdatetime.date(self._max.year, self._max.month, self._max.day) if self._max else None
        self._de = ShamsiDateEdit(
            on_change=self._sub_changed, value=jdatetime.date(v.year, v.month, v.day),
            min_date=min_d, max_date=max_d, first_year=first_year, last_year=last_year,
            calendar_popup=calendar_popup, compact=compact)
        self._te = ShamsiTimeEdit(
            on_change=self._sub_changed, value=dtime(v.hour, v.minute),
            minute_step=minute_step, compact=compact)
        self.value = v
        # wrap=True → روی صفحهٔ باریک موبایل، تاریخ و ساعت خودکار زیر هم می‌افتند
        self.body = ft.Row([self._de.body, self._te.body], spacing=8, run_spacing=6,
                           wrap=True, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _sub_changed(self, _=None):
        d, t = self._de.date(), self._te.time()
        dt = _clamp_datetime(jdatetime.datetime(d.year, d.month, d.day, t.hour, t.minute),
                             self._min, self._max)
        changed = dt != self.value
        self.value = dt
        self._de.set_date(jdatetime.date(dt.year, dt.month, dt.day))
        self._te.set_time(dtime(dt.hour, dt.minute))
        if changed and self.on_change: self.on_change(self.value)

    # — API —
    def dateTime(self): return self.value
    def date(self): return self._de.date()
    def time(self): return self._te.time()

    def set_datetime(self, dt):
        dt = _clamp_datetime(_as_datetime(dt), self._min, self._max)
        self.value = dt
        self._de.set_date(jdatetime.date(dt.year, dt.month, dt.day))
        self._te.set_time(dtime(dt.hour, dt.minute))

    @property
    def _page(self): return self._de._page
    @_page.setter
    def _page(self, p):
        self._de._page = p
        self._te._page = p


def open_date_dialog(page, value=None, on_selected=None,
                     min_date=None, max_date=None, title="انتخاب تاریخ", compact=None):
    """دیالوگ انتخاب تاریخ شمسی — روز انتخاب‌شده (jdatetime.date) به on_selected می‌رسد."""
    cal = ShamsiCalendar(value=value, min_date=min_date, max_date=max_date, compact=compact)
    cal._page = page

    def day_picked(d):
        close_dialog(page, None)
        if on_selected:
            on_selected(d)

    cal.on_change = day_picked
    dlg = _cal_dialog(page, title, cal.body,
                      [ft.TextButton("بستن", on_click=lambda e: close_dialog(page, None))])
    show_dialog(page, dlg)