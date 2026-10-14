import json
import os
from datetime import datetime

import flet as ft

from theme import elevated_card


def build_backup_view(app) -> ft.Control:
    page = app.page

    # ---------- سرویس FilePicker (یک‌بار ساخته و در page.services) ----------
    def _get_file_picker() -> ft.FilePicker:
        for s in getattr(page, "services", []):
            if isinstance(s, ft.FilePicker):
                return s
        fp = ft.FilePicker()
        page.services.append(fp)
        return fp

    # ---------- وضعیت عملیات ----------
    status_col = ft.Column(spacing=6)

    def set_status(msg: str, color: str = None, icon=ft.Icons.INFO_OUTLINE):
        status_col.controls.clear()
        status_col.controls.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=16,
                            color=color or ft.Colors.PRIMARY),
                    ft.Text(msg, size=12,
                            color=color or ft.Colors.PRIMARY,
                            expand=True),
                ], spacing=8),
                padding=10,
                bgcolor=ft.Colors.with_opacity(
                    0.08, color or ft.Colors.PRIMARY),
                border_radius=10,
            )
        )
        page.update()

    # ---------- خروجی بک‌آپ ----------
    async def export_backup(e):
        try:
            fp = _get_file_picker()
            data = app.db.export_all()
            count = len(data["chellehs"])
            default_name = (
                f"cheleh_yar_backup_"
                f"{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            )
            raw = json.dumps(data, ensure_ascii=False, indent=2)

            path = await fp.save_file(
                dialog_title="ذخیره فایل پشتیبان",
                file_name=default_name,
                allowed_extensions=["json"],
            )
            if not path:
                set_status("ذخیره لغو شد", ft.Colors.GREY, ft.Icons.INFO_OUTLINE)
                return

            if not path.endswith(".json"):
                path += ".json"

            with open(path, "w", encoding="utf-8") as f:
                f.write(raw)

            set_status(
                f"پشتیبان با موفقیت ذخیره شد ({count} چله)",
                ft.Colors.GREEN,
                ft.Icons.CHECK_CIRCLE,
            )
            app.snack("فایل پشتیبان ذخیره شد ✅")
        except Exception as ex:
            set_status(f"خطا در ذخیره: {ex}",
                       ft.Colors.RED, ft.Icons.ERROR_OUTLINE)
            app.snack("ذخیره پشتیبان ناموفق بود")

    # ---------- ورود بک‌آپ ----------
    async def import_backup(e):
        try:
            fp = _get_file_picker()
            result = await fp.pick_files(
                dialog_title="انتخاب فایل پشتیبان",
                allow_multiple=False,
                allowed_extensions=["json"],
            )
            if not result:
                set_status("انتخاب فایل لغو شد",
                           ft.Colors.GREY, ft.Icons.INFO_OUTLINE)
                return

            chosen = result[0]
            local_path = chosen.path
            # روی وب ممکن است path نباشد
            if not local_path and getattr(chosen, "bytes", None):
                content = chosen.bytes.decode("utf-8")
            else:
                with open(local_path, "r", encoding="utf-8") as f:
                    content = f.read()

            data = json.loads(content)

            # پیش‌نمایش قبل از تصمیم
            _show_import_confirm(app, data, on_done=set_status)
        except json.JSONDecodeError:
            set_status("فایل JSON نامعتبر است",
                       ft.Colors.RED, ft.Icons.ERROR_OUTLINE)
        except Exception as ex:
            set_status(f"خطا در خواندن فایل: {ex}",
                       ft.Colors.RED, ft.Icons.ERROR_OUTLINE)

    # ---------- کارت راهنما ----------
    info_card = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.INFO_OUTLINE, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("راهنما", size=14, weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Text(
                "پشتیبان شامل تمام چله‌ها، تاریخچه، یادداشت‌ها و تنظیمات "
                "برنامه است. فایل خروجی به‌صورت JSON ذخیره می‌شود و "
                "می‌توانید آن را در جای امنی نگه دارید.",
                size=12, color=ft.Colors.GREY_600,
            ),
            ft.Container(height=4),
            ft.Text(
                "⚠️ هنگام ورود پشتیبان می‌توانید انتخاب کنید که داده‌های "
                "فعلی حفظ شوند یا کاملاً جایگزین شوند.",
                size=11, color=ft.Colors.ORANGE_700,
            ),
        ], spacing=6),
        padding=16,
    )

    # ---------- دکمه‌ها ----------
    export_btn = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.DOWNLOAD,
                                color=ft.Colors.WHITE, size=24),
                width=48, height=48,
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                border_radius=12,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column([
                ft.Text("صدور پشتیبان", size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Text("ذخیره همه داده‌ها در یک فایل JSON", size=10,
                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
            ], spacing=2, expand=True),
            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=14,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
        ], spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=14, horizontal=14),
        border_radius=14,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_RIGHT,
            end=ft.Alignment.BOTTOM_LEFT,
            colors=["#1976D2", "#42A5F5"],
        ),
        shadow=ft.BoxShadow(
            blur_radius=10, spread_radius=0,
            color=ft.Colors.with_opacity(0.15, "#1976D2"),
            offset=ft.Offset(0, 4),
        ),
        ink=True,
        on_click=lambda e: page.run_task(export_backup, e),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    import_btn = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.UPLOAD_FILE,
                                color=ft.Colors.WHITE, size=24),
                width=48, height=48,
                bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                border_radius=12,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Column([
                ft.Text("ورود پشتیبان", size=14,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE),
                ft.Text("بازیابی داده‌ها از فایل پشتیبان", size=10,
                        color=ft.Colors.with_opacity(0.85, ft.Colors.WHITE)),
            ], spacing=2, expand=True),
            ft.Icon(ft.Icons.ARROW_FORWARD_IOS, size=14,
                    color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
        ], spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=ft.Padding.symmetric(vertical=14, horizontal=14),
        border_radius=14,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_RIGHT,
            end=ft.Alignment.BOTTOM_LEFT,
            colors=["#00897B", "#26A69A"],
        ),
        shadow=ft.BoxShadow(
            blur_radius=10, spread_radius=0,
            color=ft.Colors.with_opacity(0.15, "#00897B"),
            offset=ft.Offset(0, 4),
        ),
        ink=True,
        on_click=lambda e: page.run_task(import_backup, e),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    # ---------- لیست داده‌های فعلی (خلاصه) ----------
    current_data_card = elevated_card(
        ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.DATA_OBJECT, size=18,
                        color=ft.Colors.PRIMARY),
                ft.Text("وضعیت فعلی", size=14,
                        weight=ft.FontWeight.BOLD),
            ], spacing=8),
            ft.Container(height=4),
            _stat_line("تعداد چله‌ها",
                       str(len(app.chellehs))),
            _stat_line("تعداد کل روزها",
                       str(sum(len(c.daily_logs) for c in app.chellehs))),
            _stat_line("چله‌های تکمیل‌شده",
                       str(sum(1 for c in app.chellehs
                               if c.status == "completed"))),
        ], spacing=6),
        padding=16,
    )

    # ---------- UI ----------
    return ft.Column([
        ft.Container(
            content=ft.Column([
                info_card,
                ft.Container(height=14),
                export_btn,
                ft.Container(height=10),
                import_btn,
                ft.Container(height=14),
                current_data_card,
                ft.Container(height=14),
                status_col,
                ft.Container(height=24),
            ], spacing=0),
            padding=ft.Padding.symmetric(vertical=16, horizontal=16),
        ),
    ], spacing=0, scroll=ft.ScrollMode.AUTO, expand=True)


# ---------- دیالوگ تأیید ورود ----------
def _show_import_confirm(app, data: dict, on_done):
    page = app.page

    chellehs_count = len(data.get("chellehs") or [])
    exported_at = data.get("exported_at", "نامشخص")

    mode = {"replace": False}

    async def perform_import():
        try:
            added, skipped = app.db.import_all(
                data, replace=mode["replace"])
            # بارگذاری مجدد در حافظه
            app.chellehs = app.db.load_chellehs()
            app.snack(f"{added} چله وارد شد"
                      + (f" — {skipped} رد شد" if skipped else ""))
            on_done(
                f"ورود کامل شد: {added} چله اضافه شد"
                + (f"، {skipped} مورد رد شد" if skipped else ""),
                ft.Colors.GREEN, ft.Icons.CHECK_CIRCLE,
            )
            app.refresh()
        except ValueError as ex:
            on_done(str(ex), ft.Colors.RED, ft.Icons.ERROR_OUTLINE)
        except Exception as ex:
            on_done(f"خطا در ورود: {ex}",
                    ft.Colors.RED, ft.Icons.ERROR_OUTLINE)

    def set_replace(e):
        mode["replace"] = e.control.value
        page.update()

    replace_switch = ft.Switch(
        value=False,
        label="حذف داده‌های فعلی و جایگزینی کامل",
        on_change=set_replace,
    )

    def on_cancel(e):
        dialog._confirmed = False
        page.pop_dialog()

    def on_confirm(e):
        dialog._confirmed = True
        page.pop_dialog()

    def on_dismiss(e):
        if getattr(dialog, "_confirmed", False):
            page.run_task(perform_import)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.UPLOAD_FILE, color=ft.Colors.ORANGE,
                    size=26),
            ft.Text("تأیید ورود پشتیبان", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Column([
            ft.Text(
                f"این فایل شامل {chellehs_count} چله است.",
                size=13,
            ),
            ft.Text(
                f"تاریخ ساخت فایل: {exported_at[:19].replace('T', ' ')}",
                size=11, color=ft.Colors.GREY_600,
            ),
            ft.Container(height=8),
            ft.Container(
                content=replace_switch,
                padding=10,
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ORANGE),
                border_radius=10,
            ),
            ft.Text(
                "اگر این گزینه خاموش باشد، چله‌های جدید به داده‌های فعلی "
                "اضافه می‌شوند.",
                size=11, color=ft.Colors.GREY_600,
            ),
        ], spacing=6, tight=True, width=340),
        actions=[
            ft.TextButton("انصراف", on_click=on_cancel),
            ft.Button(
                "ورود داده‌ها",
                icon=ft.Icons.CHECK,
                on_click=on_confirm,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.WHITE,
                ),
            ),
        ],
        on_dismiss=on_dismiss,
    )
    dialog._confirmed = False
    page.show_dialog(dialog)


def _stat_line(label: str, value: str) -> ft.Row:
    return ft.Row([
        ft.Text(label, size=12, color=ft.Colors.GREY_600, expand=True),
        ft.Text(value, size=13, weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY),
    ], spacing=4)