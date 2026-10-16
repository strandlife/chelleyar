import flet as ft
import json
import base64
from utils import to_persian_digits
from views.lock_dialogs import show_unlock_dialog



# ==================================================================
# اشتراک‌گذاری چله
# ==================================================================

SHARE_PREFIX = "CHELEHYAR1:"

def _card_actions(app, c, is_locked: bool) -> list[ft.Control]:
    """اکشن‌های انتهای کارت — همان الگوی appbar:
    دسکتاپ: آیکن‌های مستقیم
    موبایل: منوی سه‌نقطه
    """
    page = app.page

    # ---------- هندلرهای مشترک ----------
    def go_edit(e):
        if is_locked:
            app.snack("ابتدا چله را باز کنید")
            return
        app.open_edit(c)

    def go_stats(e):
        if is_locked:
            app.snack("ابتدا چله را باز کنید")
            return
        app.open_stats(c)

    def go_share(e):
        if is_locked:
            app.snack("چله‌های قفل‌شده قابل اشتراک‌گذاری نیستند")
            return
        _show_share_dialog(app, c)

    def go_unlock(e):
        _show_unlock_dialog(app, c)

    def go_lock(e):
        """قفل کردن چله — نیاز به تعیین رمز"""
        from views.lock_dialogs import show_lock_dialog
        show_lock_dialog(app, c)

    def go_remove_lock(e):
        """برداشتن قفل — چله در حافظه باید باز باشد"""
        from views.lock_dialogs import show_remove_lock_dialog
        show_remove_lock_dialog(app, c)

    def go_delete(e):
        _show_delete_dialog(app, c)

    # ---------- دسکتاپ: آیکن‌های مستقیم ----------
    if app.is_desktop():
        if is_locked:
            # چله قفل است: باز کردن + حذف
            return [
                ft.IconButton(
                    ft.Icons.LOCK_OPEN,
                    icon_size=20,
                    icon_color=ft.Colors.PRIMARY,
                    tooltip="باز کردن چله",
                    on_click=go_unlock,
                ),
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_size=20,
                    icon_color=ft.Colors.RED_400,
                    tooltip="حذف چله",
                    on_click=go_delete,
                ),
            ]

        # چله باز است: چهار دکمه اصلی + بر اساس حالت قفل، آیکون قفل
        actions = [
            ft.IconButton(
                ft.Icons.EDIT_OUTLINED,
                icon_size=20,
                icon_color=ft.Colors.PRIMARY,
                tooltip="ویرایش چله",
                on_click=go_edit,
            ),
            ft.IconButton(
                ft.Icons.INSIGHTS_OUTLINED,
                icon_size=20,
                icon_color=ft.Colors.ORANGE,
                tooltip="آمار و گزارش",
                on_click=go_stats,
            ),
            ft.IconButton(
                ft.Icons.SHARE_OUTLINED,
                icon_size=18,
                icon_color=ft.Colors.BLUE_400,
                tooltip="اشتراک‌گذاری چله",
                on_click=go_share,
            ),
        ]

        # آیکون قفل: اگر چله رمزنگاری‌شده و باز است → «برداشتن قفل»
        #            اگر رمزنگاری‌نشده است → «قفل کردن با رمز»
        if c.encrypted:
            actions.append(
                ft.IconButton(
                    ft.Icons.LOCK_OUTLINE,
                    icon_size=20,
                    icon_color=ft.Colors.INDIGO,
                    tooltip="برداشتن قفل",
                    on_click=go_remove_lock,
                )
            )
        else:
            actions.append(
                ft.IconButton(
                    ft.Icons.LOCK,
                    icon_size=20,
                    icon_color=ft.Colors.INDIGO,
                    tooltip="قفل کردن با رمز",
                    on_click=go_lock,
                )
            )

        actions.append(
            ft.IconButton(
                ft.Icons.DELETE_OUTLINE,
                icon_size=20,
                icon_color=ft.Colors.RED_400,
                tooltip="حذف چله",
                on_click=go_delete,
            )
        )
        return actions

    # ---------- موبایل: منوی سه‌نقطه ----------
    def open_menu(e):
        if is_locked:
            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LOCK_OPEN,
                                    color=ft.Colors.PRIMARY),
                    title=ft.Text("باز کردن چله"),
                    on_click=lambda ev: (page.pop_dialog(), go_unlock(ev)),
                ),
                ft.Divider(height=1),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DELETE_OUTLINE,
                                    color=ft.Colors.RED_400),
                    title=ft.Text("حذف چله", color=ft.Colors.RED_400),
                    on_click=lambda ev: (page.pop_dialog(), go_delete(ev)),
                ),
            ]
        else:
            items = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.EDIT_OUTLINED,
                                    color=ft.Colors.PRIMARY),
                    title=ft.Text("ویرایش چله"),
                    on_click=lambda ev: (page.pop_dialog(), go_edit(ev)),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.INSIGHTS_OUTLINED,
                                    color=ft.Colors.ORANGE),
                    title=ft.Text("آمار و گزارش"),
                    on_click=lambda ev: (page.pop_dialog(), go_stats(ev)),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SHARE_OUTLINED,
                                    color=ft.Colors.BLUE_400),
                    title=ft.Text("اشتراک‌گذاری چله"),
                    on_click=lambda ev: (page.pop_dialog(), go_share(ev)),
                ),
                # گزینه‌ی قفل بر اساس وضعیت فعلی
                ft.ListTile(
                    leading=ft.Icon(
                        ft.Icons.LOCK_OUTLINE if c.encrypted else ft.Icons.LOCK,
                        color=ft.Colors.INDIGO,
                    ),
                    title=ft.Text(
                        "برداشتن قفل" if c.encrypted else "قفل کردن با رمز"
                    ),
                    on_click=lambda ev: (
                        page.pop_dialog(),
                        (go_remove_lock if c.encrypted else go_lock)(ev),
                    ),
                ),
                ft.Divider(height=1),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.DELETE_OUTLINE,
                                    color=ft.Colors.RED_400),
                    title=ft.Text("حذف چله", color=ft.Colors.RED_400),
                    on_click=lambda ev: (page.pop_dialog(), go_delete(ev)),
                ),
            ]

        dialog = ft.AlertDialog(
            content=ft.Column(items, spacing=0, tight=True, width=260),
            content_padding=ft.Padding.symmetric(vertical=8, horizontal=0),
        )
        page.show_dialog(dialog)

    return [
        ft.IconButton(
            ft.Icons.MORE_VERT,
            icon_size=20,
            icon_color=ft.Colors.GREY_500,
            tooltip="گزینه‌ها",
            on_click=open_menu,
        ),
    ]

def make_share_code(c) -> str:
    """کد اشتراک‌گذاری چله — فقط تعریف چله، بدون داده‌های شخصی."""
    payload = {
        "name": c.name,
        "display_name": c.display_name,
        "task": c.task,
        "levels": c.levels,
        "total_days": c.total_days,
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return SHARE_PREFIX + base64.urlsafe_b64encode(
        raw.encode("utf-8")).decode("ascii")


def _get_service(page: ft.Page, service_type):
    """سرویس موردنظر را از page.services برمی‌گرداند؛ اگر نبود می‌سازد."""
    for s in getattr(page, "services", []):
        if isinstance(s, service_type):
            return s
    svc = service_type()
    page.services.append(svc)
    return svc


def _show_share_dialog(app, c):
    page = app.page
    code = make_share_code(c)

    code_field = ft.TextField(
        value=code,
        read_only=True,
        multiline=True,
        min_lines=4,
        max_lines=6,
        border_radius=ft.BorderRadius.all(12),
        filled=True,
    )

    # ------- حالت‌های دیالوگ -------
    # action["value"] می‌تواند None, "copy" یا "close" باشد
    action = {"value": None}

    async def perform_copy():
        try:
            clipboard = _get_service(page, ft.Clipboard)
            await clipboard.set(code)
            app.snack("کد اشتراک‌گذاری کپی شد ✅")
        except Exception:
            app.snack("کپی نشد — متن کد را دستی انتخاب و کپی کنید")

    share_message = (
        f"چله «{c.display_name}» را برای تو فرستادم 🌱\n"
        f"این کد را در اپ «چله‌یار» وارد کن:\n\n{code}"
    )

    def on_dismiss(e):
        val = action.get("value")
        if val == "copy":
            page.run_task(perform_copy)
        # برای ارسال (share) کار دیگری لازم نیست —
        # چون ShareText به‌صورت سمت-کلاینت اجرا شده.

    def on_cancel(e):
        action["value"] = None
        page.pop_dialog()

    def on_copy(e):
        action["value"] = "copy"
        page.pop_dialog()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.SHARE, size=20, color=ft.Colors.PRIMARY),
            ft.Text("اشتراک‌گذاری چله", size=16,
                    weight=ft.FontWeight.BOLD),
        ], spacing=8),
        content=ft.Container(
            width=300,
            content=ft.Column([
                ft.Text(
                    "این کد شامل تعریف چله (نام، وظیفه و سطوح) است. "
                    "سابقه و یادداشت‌های شخصی شما ارسال نمی‌شود.",
                    size=11, color=ft.Colors.GREY_600),
                code_field,
                ft.Text(
                    "کد را کپی کنید و برای دوستتان بفرستید.",
                    size=10, color=ft.Colors.GREY_500),
            ], tight=True, spacing=10),
        ),
        actions=[
            ft.TextButton("انصراف", on_click=on_cancel),
            ft.TextButton(
                "کپی کد",
                icon=ft.Icons.COPY,
                on_click=on_copy,
            ),
            ft.Button(
                "ارسال",
                icon=ft.Icons.SHARE,
                action=ft.ShareText(
                    share_message,
                    subject="چله‌یار",
                ),
                # روی وب این دکمه بعد از اجرای ShareText بسته نمی‌شود
                # مگر اینکه کاربر بعداً خودش ببندد.
                on_click=on_cancel,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                ),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=on_dismiss,
    )
    page.show_dialog(dialog)

# نوار فرایند چندرنگ (ترکیب سطح + پیشرفت)
# ==================================================================

def _get_day_state(c, day: int):
    """(رنگ، tooltip) وضعیت یک روز مشخص برای نوار چندرنگ."""
    log = c.daily_logs.get(str(day))

    # روزِ ثبت‌شده با نتیجه مشخص
    if log and log.get("result"):
        idx = log.get("level_index")
        if log["result"] == "success":
            if isinstance(idx, int) and 0 <= idx < len(c.levels or []):
                lv = c.levels[idx]
                return (lv.get("color", "#4CAF50"),
                        f"روز {day}: {lv.get('title') or 'بدون عنوان'} — موفق ✅")
            return "#2E7D32", f"روز {day}: موفق ✅"
        # شکست
        if not (isinstance(idx, int) and 0 <= idx < len(c.levels or [])):
            idx = c.failure_level_index()
        title = "بدون عنوان"
        if isinstance(idx, int) and 0 <= idx < len(c.levels or []):
            title = c.levels[idx].get("title") or "بدون عنوان"
        return ft.Colors.RED_400, f"روز {day}: {title} — شکست ❌"

    # صبح/شب ثبت شده ولی نتیجه هنوز مشخص نیست
    if log and (log.get("morning_saved") or log.get("evening_saved")):
        idx = log.get("level_index")
        if isinstance(idx, int) and 0 <= idx < len(c.levels or []):
            lv = c.levels[idx]
            return (ft.Colors.with_opacity(0.5, lv.get("color", "#4CAF50")),
                    f"روز {day}: {lv.get('title')} — در انتظار نتیجه ⏳")
        return ft.Colors.AMBER_400, f"روز {day}: در انتظار نتیجه ⏳"

    # امروز — هنوز چیزی ثبت نشده
    if day == c.current_day and c.status != "completed":
        return ft.Colors.PRIMARY, f"روز {day} — امروز 📍"

    # روزهای آینده
    return ft.Colors.with_opacity(0.18, ft.Colors.GREY), f"روز {day}"


def build_level_bar(c, height: int = 10, expand: bool = False) -> ft.Control:
    """نوار فرایند چندرنگ — هر روز یک قطعه به رنگِ سطحِ همان روز.

    ⚠️ expand=True فقط وقتی معنا دارد که نوار داخل یک Row افقی باشد.
    """
    if not c.total_days:
        bar = ft.Container(height=height)
        bar.expand = expand
        return bar

    segments = []
    for day in range(1, c.total_days + 1):
        color, tip = _get_day_state(c, day)
        seg = ft.Container(expand=True, bgcolor=color, tooltip=tip)

        # حلقه دور قطعه‌ی «امروز»
        if day == c.current_day and c.status != "completed":
            ring = (ft.Colors.with_opacity(0.55, ft.Colors.WHITE)
                    if color == ft.Colors.PRIMARY else ft.Colors.PRIMARY)
            seg.border = ft.Border.all(1.5, ring)

        segments.append(seg)

    bar = ft.Container(
        content=ft.Row(
            segments,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
        height=height,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREY),
        border_radius=height / 2,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
    )
    bar.expand = expand
    return bar


def _legend_dot(color: str, text: str) -> ft.Control:
    return ft.Row(
        [
            ft.Container(width=8, height=8, bgcolor=color, border_radius=4),
            ft.Text(text, size=9, color=ft.Colors.GREY_600,
                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
        ],
        spacing=4, tight=True,
    )


def build_level_legend(c) -> ft.Control:
    """راهنمای رنگ‌های نوار — جایگزین «بخش سطح» قبلی."""
    items = [
        _legend_dot(lv.get("color", "#4CAF50"),
                    lv.get("title") or "بدون عنوان")
        for lv in (c.levels or [])
    ]
    items.append(_legend_dot(ft.Colors.RED_400, "شکست"))
    items.append(_legend_dot(ft.Colors.PRIMARY, "امروز"))
    return ft.Row(items, spacing=10, wrap=True, run_spacing=4)
    
def get_level_info(c) -> dict:
    """اطلاعات سطح اجرای «روز جاری» را برای نمایش برمی‌گرداند.

    حالت‌ها:
      {"mode": "done"}     → چله تکمیل شده
      {"mode": "empty"}    → امروز هنوز چیزی ثبت نشده
      {"mode": "pending"}  → سطح ثبت شده، نتیجه صبح/شب هنوز مشخص نیست
      {"mode": "success"}  → روز موفق
      {"mode": "failure"}  → روز ناموفق
    کلید «level» در سه حالت آخر مقدار دارد.
    """
    if c.status == "completed":
        return {"mode": "done"}

    log = c.daily_logs.get(str(c.current_day))

    has_content = bool(log) and (
        log.get("morning_saved") or log.get("evening_saved")
        or log.get("result")
    )
    if not has_content:
        return {"mode": "empty"}

    # سطح از level_index (ایندکس واقعی انتخاب کاربر)
    level = None
    idx = log.get("level_index")
    if isinstance(idx, int) and 0 <= idx < len(c.levels or []):
        level = c.levels[idx]

    result = log.get("result")
    if result == "success":
        mode = "success"
    elif result:  # هر مقدار دیگر (مثل "failure")
        mode = "failure"
        # اگر level_index معتبر نبود، سطح شکست را از خود مدل بگیر
        if level is None:
            fi = c.failure_level_index()
            if 0 <= fi < len(c.levels or []):
                level = c.levels[fi]
    else:
        mode = "pending"

    return {"mode": mode, "level": level, "score": log.get("score", 0)}


# ==================================================================
# کارت چله
# ==================================================================
def build_chelleh_card(app, c) -> ft.Control:
    day = c.current_day
    prog = c.progress()
    is_done = c.status == "completed"
    ratio = prog / c.total_days if c.total_days else 0
    accent = "#2E7D32" if is_done else ft.Colors.PRIMARY

    is_locked = c.encrypted and not app.is_unlocked(c)

    # ---------- اطلاعات نمایشی بر اساس حالت قفل ----------
    if is_locked:
        title = f"چله قفل‌شده #{c.id[:6]}"
        subtitle = "برای مشاهده، رمز عبور را وارد کنید"
        circle_content = ft.Icon(ft.Icons.LOCK, color=ft.Colors.WHITE, size=22)
        circle_bg = ft.Colors.GREY_600
    else:
        title = c.display_name or c.name or "بدون نام"
        subtitle = c.task or ""
        if is_done:
            circle_content = ft.Icon(ft.Icons.CHECK,
                                     color=ft.Colors.WHITE, size=22)
            circle_bg = "#2E7D32"
        else:
            circle_content = ft.Text(
                to_persian_digits(str(day)),
                size=16,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            )
            circle_bg = ft.Colors.PRIMARY

    # ---------- کلیک روی کارت ----------
    def on_card_click(e):
        if is_locked:
            show_unlock_dialog(app, c)
        else:
            app.open_status(c)

    # ---------- عنوان + برچسب تکمیل ----------
    title_row_children = [
        ft.Text(
            title,
            size=15,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
            expand=True,
        ),
    ]
    if is_done and not is_locked:
        title_row_children.append(
            ft.Container(
                content=ft.Text(
                    "تکمیل",
                    size=9,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
                padding=ft.Padding.symmetric(vertical=3, horizontal=8),
                bgcolor="#2E7D32",
                border_radius=8,
            )
        )
    if is_locked:
        title_row_children.append(
            ft.Container(
                content=ft.Text(
                    "قفل",
                    size=9,
                    color=ft.Colors.WHITE,
                    weight=ft.FontWeight.BOLD,
                ),
                padding=ft.Padding.symmetric(vertical=3, horizontal=8),
                bgcolor=ft.Colors.GREY_700,
                border_radius=8,
            )
        )

    title_row = ft.Row(
        title_row_children,
        spacing=6,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # ---------- نوار فرایند ----------
    # برای چله قفل‌شده نوار پیشرفت را هم مخفی می‌کنیم
    # چون بر اساس سطوح رمزنگاری‌شده ساخته می‌شود
    if is_locked:
        bar_row = ft.Container(height=6)
    else:
        bar_row = ft.Row(
            [
                build_level_bar(c, height=10, expand=True),
                ft.Text(
                    to_persian_digits(f"{int(ratio * 100)}٪"),
                    size=10,
                    color=accent,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ---------- اکشن‌های کارت ----------
    actions = _card_actions(app, c, is_locked)

    # ---------- کارت اصلی ----------
    card = ft.Container(
        content=ft.Row([
            ft.Container(
                content=circle_content,
                width=52, height=52,
                bgcolor=circle_bg,
                border_radius=26,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column([
                ft.Row([
                    ft.Column([
                        title_row,
                        ft.Text(
                            subtitle,
                            size=11,
                            color=ft.Colors.GREY_600,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ], expand=True),
                    *actions,
                ]),
                bar_row,
            ], spacing=3, expand=True),
        ], spacing=10),
        padding=ft.Padding.symmetric(vertical=12, horizontal=12),
        border_radius=16,
        bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,
        shadow=ft.BoxShadow(
            blur_radius=8, spread_radius=0,
            color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        ),
        ink=True,
        on_click=on_card_click,
    )

    return card



def _show_delete_dialog(app, ch):
    page = app.page

    async def perform_delete():
        app.chellehs = [x for x in app.chellehs if x.id != ch.id]
        app.db.delete_chelleh(ch.id)
        app.snack("چله حذف شد")
        app.refresh()

    def on_dismiss(e):
        if getattr(dialog, "_confirmed", False):
            page.run_task(perform_delete)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.RED, size=26),
            ft.Text("حذف چله", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Text(
            f"آیا از حذف «{ch.display_name}» مطمئن هستید؟\n"
            "تمام تاریخچه و یادداشت‌ها پاک می‌شوند.",
            size=13,
        ),
        actions=[
            ft.TextButton(
                "انصراف",
                on_click=lambda e: (setattr(dialog, "_confirmed", False),
                                    page.pop_dialog()),
            ),
            ft.Button(
                "حذف",
                icon=ft.Icons.DELETE,
                on_click=lambda e: (setattr(dialog, "_confirmed", True),
                                    page.pop_dialog()),
                style=ft.ButtonStyle(bgcolor=ft.Colors.RED,
                                     color=ft.Colors.WHITE),
            ),
        ],
        on_dismiss=on_dismiss,
    )
    dialog._confirmed = False
    page.show_dialog(dialog)