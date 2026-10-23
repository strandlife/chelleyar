# flet_shamsi_qt.py — ویجت‌های تاریخ/زمان شمسی برای Flet 1، به سبک PySide6
from __future__ import annotations
from datetime import datetime, time as dtime, timedelta

import flet as ft
import jdatetime

__all__ = ["ShamsiCalendar", "ShamsiDateEdit", "ShamsiTimeEdit", "ShamsiDateTimeEdit",
           "format_jdate", "format_time", "parse_jdate", "parse_time"]

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

def _shift_time(t, minutes):
    total = (t.hour * 60 + t.minute + minutes) % (24 * 60)
    return t.replace(hour=total // 60, minute=total % 60)

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

_CELL_W, _CELL_H = 44, 36

# ───────────────────── ۱) ShamsiCalendar ≈ QCalendarWidget ─────────────────────

class ShamsiCalendar:
    def __init__(self, on_change=None, value=None, min_date=None, max_date=None,
                 first_year=1300, last_year=1500, show_today_button=True):
        self.on_change = on_change
        self._page = None
        self._min, self._max = min_date, max_date
        self.first_year, self.last_year = first_year, last_year
        self.show_today_button = show_today_button
        self.value = _clamp_date(value or jdatetime.date.today(), min_date, max_date)
        self._vy, self._vm = self.value.year, self.value.month
        self.body = ft.Column(spacing=6, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self._render()

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

    def show_today(self):     self.set_date(jdatetime.date.today())
    def next_month(self):     self._nav(+1)
    def previous_month(self): self._nav(-1)

    # — داخلی —
    def _page_update(self):
        self._render()
        if self._page: self._page.update()

    def _nav(self, delta):
        m, y = self._vm + delta, self._vy
        if m == 0:   m, y = 12, y - 1
        elif m == 13: m, y = 1, y + 1
        self._vy, self._vm = y, m
        self._page_update()

    def _render(self):
        controls = [self._header(), self._weekdays(), self._grid()]
        if self.show_today_button:
            controls.append(self._today_row())
        self.body.controls = controls

    def _header(self):
        y_lo, y_hi = min(self.first_year, self._vy), max(self.last_year, self._vy)
        return ft.Row([
            ft.IconButton(ft.Icons.CHEVRON_LEFT, tooltip="ماه قبل", on_click=lambda e: self._nav(-1)),
            ft.Dropdown(width=110, value=str(self._vm),
                        options=[ft.DropdownOption(key=str(m), text=J_MONTHS[m - 1]) for m in range(1, 13)],
                        on_select=lambda e: self._view(int(e.control.value), self._vy)),
            ft.Dropdown(width=90, value=str(self._vy),
                        options=[ft.DropdownOption(key=str(y), text=fa(y)) for y in range(y_lo, y_hi + 1)],
                        on_select=lambda e: self._view(self._vm, int(e.control.value))),
            ft.IconButton(ft.Icons.CHEVRON_RIGHT, tooltip="ماه بعد", on_click=lambda e: self._nav(+1)),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _view(self, m, y):
        self._vm, self._vy = m, y
        self._page_update()

    def _weekdays(self):
        return ft.Row(
            [ft.Row([ft.Text(w, size=13, weight=ft.FontWeight.BOLD)],
                    width=_CELL_W, alignment=ft.MainAxisAlignment.CENTER)
             for w in reversed(J_WEEKDAYS_SHORT)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=2)

    def _grid(self):
        offset = jdatetime.date(self._vy, self._vm, 1).weekday()   # شنبه = ۰
        spacer = lambda: ft.Container(width=_CELL_W, height=_CELL_H)
        cells = [spacer() for _ in range(offset)]
        cells += [self._day_cell(d) for d in range(1, _days_in_month(self._vy, self._vm) + 1)]
        rows = [cells[i:i + 7] for i in range(0, len(cells), 7)]
        rows[-1] += [spacer() for _ in range(7 - len(rows[-1]))]
        return ft.Column([ft.Row(r[::-1], alignment=ft.MainAxisAlignment.CENTER, spacing=2)
                          for r in rows], spacing=2)

    def _day_cell(self, day):
        d = jdatetime.date(self._vy, self._vm, day)
        disabled = (self._min and d < self._min) or (self._max and d > self._max)
        if d == self.value:
            st = ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, padding=0)
        elif d == jdatetime.date.today():
            st = ft.ButtonStyle(bgcolor=ft.Colors.BLUE_100, color=ft.Colors.BLUE_900, padding=0)
        else:
            st = ft.ButtonStyle(padding=0)
        return ft.TextButton(fa(day), width=_CELL_W, height=_CELL_H, style=st,
                             disabled=disabled, on_click=lambda e, dd=day: self.set_date(
                                 jdatetime.date(self._vy, self._vm, dd)))

    def _today_row(self):
        return ft.Row([ft.TextButton("امروز", on_click=lambda e: self.show_today())],
                      width=7 * _CELL_W + 12, alignment=ft.MainAxisAlignment.END)

# ───────────────────── ۲) ShamsiDateEdit ≈ QDateEdit ─────────────────────

# ───────────────────── ۲) ShamsiDateEdit ≈ QDateEdit (بخش‌محور) ─────────────────────

class ShamsiDateEdit:
    def __init__(self, on_change=None, value=None, min_date=None, max_date=None,
                 first_year=1300, last_year=1500, calendar_popup=True):
        self.on_change = on_change
        self._page = None
        self._min, self._max = min_date, max_date
        self.first_year, self.last_year = first_year, last_year
        self._section = "day"
        self._dlg = None
        self.value = _clamp_date(value or jdatetime.date.today(), min_date, max_date)

        self.f_y = self._make_field("year", 60)
        self.f_m = self._make_field("month", 52)
        self.f_d = self._make_field("day", 52)
        sep = lambda ch: ft.Text(ch, size=15, weight=ft.FontWeight.BOLD)
        parts = [self.f_y, sep("/"), self.f_m, sep("/"), self.f_d, self._spin()]
        if calendar_popup:
            parts.append(ft.IconButton(ft.Icons.CALENDAR_MONTH, tooltip="تقویم", on_click=self.open_popup))
        self.body = ft.Row(parts, spacing=3, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self._refresh()

    def _make_field(self, sec, w):
        return ft.TextField(value="", width=w, dense=True, text_align=ft.TextAlign.CENTER,
                            on_focus=lambda e, s=sec: self._set_section(s),
                            on_blur=self._apply_all, on_submit=self._apply_all)

    def _set_section(self, sec): self._section = sec

    def _spin(self):
        return ft.Column([
            ft.IconButton(ft.Icons.ARROW_DROP_UP, width=34, height=20, style=ft.ButtonStyle(padding=0),
                          tooltip="زیاد کردن بخش انتخاب‌شده", on_click=lambda e: self._step_section(+1)),
            ft.IconButton(ft.Icons.ARROW_DROP_DOWN, width=34, height=20, style=ft.ButtonStyle(padding=0),
                          tooltip="کم کردن بخش انتخاب‌شده", on_click=lambda e: self._step_section(-1)),
        ], spacing=0)

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
        if self._page: self._page.update()

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
        else:  # day — مثل Qt به ماه/سال بعد می‌غلتد
            nd = _shift_date(jdatetime.date(y, m, d), delta)
            y, m, d = nd.year, nd.month, nd.day
        self.set_date(jdatetime.date(y, m, d))

    def open_popup(self, e=None):
        cal = ShamsiCalendar(on_change=self._picked, value=self.value,
                             min_date=self._min, max_date=self._max)
        cal._page = self._page
        self._dlg = ft.AlertDialog(modal=True, title=ft.Text("انتخاب تاریخ"), content=cal.body,
                                   actions=[ft.TextButton("بستن", on_click=self.close_popup)])
        show_dialog(self._page, self._dlg)

    def close_popup(self, e=None): close_dialog(self._page, self._dlg)

    def _picked(self, d):
        self.close_popup()
        self.set_date(d)

# ───────────────────── ۳) ShamsiTimeEdit ≈ QTimeEdit (بخش‌محور) ─────────────────────

class ShamsiTimeEdit:
    def __init__(self, on_change=None, value=None, minute_step=1):
        self.on_change = on_change
        self._page = None
        self._step_min = minute_step
        self._section = "minute"
        self.value = value or dtime(0, 0)

        self.f_h = self._make_field("hour", 48)
        self.f_m = self._make_field("minute", 52)
        parts = [self.f_h, ft.Text(":", size=15, weight=ft.FontWeight.BOLD), self.f_m, self._spin()]
        self.body = ft.Row(parts, spacing=3, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self._refresh()

    def _make_field(self, sec, w):
        return ft.TextField(value="", width=w, dense=True, text_align=ft.TextAlign.CENTER,
                            on_focus=lambda e, s=sec: self._set_section(s),
                            on_blur=self._apply_all, on_submit=self._apply_all)

    def _set_section(self, sec): self._section = sec

    def _spin(self):
        return ft.Column([
            ft.IconButton(ft.Icons.ARROW_DROP_UP, width=34, height=20, style=ft.ButtonStyle(padding=0),
                          tooltip="زیاد کردن بخش انتخاب‌شده", on_click=lambda e: self._step_section(+1)),
            ft.IconButton(ft.Icons.ARROW_DROP_DOWN, width=34, height=20, style=ft.ButtonStyle(padding=0),
                          tooltip="کم کردن بخش انتخاب‌شده", on_click=lambda e: self._step_section(-1)),
        ], spacing=0)

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
        if self._page: self._page.update()

    def _step_section(self, delta):
        h, mi = self.value.hour, self.value.minute
        if self._section == "hour":
            h = (h + delta) % 24            # مثل Qt: wrap مستقل، بدون دست‌کاری دقیقه
        else:
            mi = (mi + delta * self._step_min) % 60
        self.set_time(dtime(h, mi))

# ───────────────────── ۴) ShamsiDateTimeEdit ≈ QDateTimeEdit ─────────────────────

class ShamsiDateTimeEdit:
    def __init__(self, on_change=None, value=None, min_datetime=None, max_datetime=None,
                 calendar_popup=True, minute_step=1, first_year=1300, last_year=1500):
        self.on_change = on_change
        self._min = _as_datetime(min_datetime)
        self._max = _as_datetime(max_datetime)
        v = _clamp_datetime(_as_datetime(value) or jdatetime.datetime.today(), self._min, self._max)
        min_d = jdatetime.date(self._min.year, self._min.month, self._min.day) if self._min else None
        max_d = jdatetime.date(self._max.year, self._max.month, self._max.day) if self._max else None
        self._de = ShamsiDateEdit(on_change=self._sub_changed, value=jdatetime.date(v.year, v.month, v.day),
                                  min_date=min_d, max_date=max_d,
                                  first_year=first_year, last_year=last_year,
                                  calendar_popup=calendar_popup)
        self._te = ShamsiTimeEdit(on_change=self._sub_changed, value=dtime(v.hour, v.minute),
                                  minute_step=minute_step)
        self.value = v
        self.body = ft.Row([self._de.body, self._te.body], spacing=10,
                           vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _sub_changed(self, _=None):
        d, t = self._de.date(), self._te.time()
        dt = _clamp_datetime(jdatetime.datetime(d.year, d.month, d.day, t.hour, t.minute),
                             self._min, self._max)
        changed = dt != self.value
        self.value = dt
        self._de.set_date(jdatetime.date(dt.year, dt.month, dt.day))   # بازتاب clamp
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
                     min_date=None, max_date=None, title="انتخاب تاریخ"):
    """دیالوگ انتخاب تاریخ شمسی — روز انتخاب‌شده (jdatetime.date) به on_selected می‌رسد."""
    cal = ShamsiCalendar(value=value, min_date=min_date, max_date=max_date)
    cal._page = page

    def day_picked(d):
        page.pop_dialog()            # بستن دیالوگ بعد از انتخاب روز
        if on_selected:
            on_selected(d)

    cal.on_change = day_picked
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=cal.body,
        actions=[ft.TextButton("بستن", on_click=lambda e: page.pop_dialog())],
    )
    show_dialog(page, dlg)