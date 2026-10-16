import flet as ft
from crypto import encrypt_chelleh


def show_unlock_dialog(app, ch):
    """دیالوگ ورود رمز برای باز کردن چله قفل‌شده"""
    page = app.page

    password_field = ft.TextField(
        label="رمز عبور",
        password=True,
        can_reveal_password=True,
        autofocus=True,
        filled=True,
        border_radius=12,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
    )

    error_text = ft.Text("", size=11, color=ft.Colors.RED, visible=False)

    async def perform_unlock():
        from crypto import decrypt_chelleh
        pw = password_field.value or ""
        if not pw:
            app.snack("رمز عبور را وارد کنید")
            return
        if decrypt_chelleh(ch, pw):
            app.unlocked[ch.id] = pw
            app.snack("چله باز شد 🔓")
            app.refresh()
        else:
            app.snack("رمز عبور اشتباه است ❌")

    def on_confirm(e):
        if not (password_field.value or "").strip():
            error_text.value = "رمز عبور را وارد کنید"
            error_text.visible = True
            page.update()
            return
        dialog._confirmed = True
        page.pop_dialog()

    def on_cancel(e):
        dialog._confirmed = False
        page.pop_dialog()

    def on_dismiss(e):
        if getattr(dialog, "_confirmed", False):
            page.run_task(perform_unlock)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.LOCK_OUTLINE, color=ft.Colors.PRIMARY, size=24),
            ft.Text("باز کردن چله", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Column([
            ft.Text("این چله با رمز عبور محافظت می‌شود.",
                    size=12, color=ft.Colors.GREY_600),
            password_field,
            error_text,
        ], tight=True, spacing=10, width=320),
        actions=[
            ft.TextButton("انصراف", on_click=on_cancel),
            ft.Button(
                "باز کردن",
                icon=ft.Icons.LOCK_OPEN,
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


def show_lock_dialog(app, ch):
    """دیالوگ تعیین رمز جدید برای قفل کردن یک چله"""
    page = app.page

    pw1 = ft.TextField(
        label="رمز عبور",
        password=True,
        can_reveal_password=True,
        filled=True,
        border_radius=12,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
    )
    pw2 = ft.TextField(
        label="تکرار رمز عبور",
        password=True,
        can_reveal_password=True,
        filled=True,
        border_radius=12,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
    )

    hint_text = ft.Text(
        "⚠️ رمز را جای امنی نگه دارید. اگر فراموش شود، "
        "داده‌های این چله برای همیشه غیرقابل بازیابی خواهند بود.",
        size=10, color=ft.Colors.ORANGE_800,
    )

    async def perform_lock():
        p1 = pw1.value or ""
        p2 = pw2.value or ""
        if len(p1) < 4:
            app.snack("رمز باید حداقل ۴ کاراکتر باشد")
            return
        if p1 != p2:
            app.snack("رمز و تکرار آن یکسان نیستند")
            return

        encrypt_chelleh(ch, p1)
        app.unlocked.pop(ch.id, None)
        app.db.save_chelleh(ch)
        app.snack("چله قفل شد 🔒")
        app.refresh()

    def on_confirm(e):
        dialog._confirmed = True
        page.pop_dialog()

    def on_cancel(e):
        dialog._confirmed = False
        page.pop_dialog()

    def on_dismiss(e):
        if getattr(dialog, "_confirmed", False):
            page.run_task(perform_lock)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.LOCK, color=ft.Colors.PRIMARY, size=24),
            ft.Text("قفل کردن چله", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Column([
            ft.Text("رمز عبوری تعیین کنید تا این چله محافظت شود.",
                    size=12, color=ft.Colors.GREY_600),
            pw1,
            pw2,
            hint_text,
        ], tight=True, spacing=10, width=340),
        actions=[
            ft.TextButton("انصراف", on_click=on_cancel),
            ft.Button(
                "قفل کن",
                icon=ft.Icons.LOCK,
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


def show_remove_lock_dialog(app, ch):
    """دیالوگ حذف قفل — پس از تأیید، چله کاملاً آزاد می‌شود"""
    page = app.page

    async def perform_remove():
        # چله در حافظه باز است، فقط فیلدها را پاک می‌کنیم
        ch.encrypted = False
        ch.ciphertext = ""
        ch.salt = ""
        app.unlocked.pop(ch.id, None)
        app.db.save_chelleh(ch)
        app.snack("قفل چله برداشته شد 🔓")
        app.refresh()

    def on_confirm(e):
        dialog._confirmed = True
        page.pop_dialog()

    def on_cancel(e):
        dialog._confirmed = False
        page.pop_dialog()

    def on_dismiss(e):
        if getattr(dialog, "_confirmed", False):
            page.run_task(perform_remove)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_AMBER, color=ft.Colors.ORANGE,
                    size=26),
            ft.Text("برداشتن قفل", weight=ft.FontWeight.BOLD),
        ]),
        content=ft.Text(
            "با این کار، چله بدون رمز عبور در دسترس خواهد بود "
            "و داده‌های آن روی دستگاه شما آزاد ذخیره می‌شود.\n\n"
            "آیا مطمئن هستید؟",
            size=13,
        ),
        actions=[
            ft.TextButton("انصراف", on_click=on_cancel),
            ft.Button(
                "برداشتن قفل",
                icon=ft.Icons.LOCK_OPEN,
                on_click=on_confirm,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.ORANGE,
                    color=ft.Colors.WHITE,
                ),
            ),
        ],
        on_dismiss=on_dismiss,
    )
    dialog._confirmed = False
    page.show_dialog(dialog)