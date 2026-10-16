import base64
import json
import os
from dataclasses import asdict

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


SALT_SIZE = 16
PBKDF2_ITERATIONS = 200_000

# فیلدهایی که داخل ciphertext رمزنگاری می‌شوند
SENSITIVE_FIELDS = (
    "name",
    "display_name",
    "task",
    "levels",
    "daily_logs",
    "history",
)


def _derive_key(password: str, salt: bytes) -> bytes:
    """مشتق‌سازی کلید Fernet از رمز عبور و salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def encrypt_chelleh(chelleh, password: str) -> None:
    """محتوای حساس چله را رمزنگاری و در فیلدهای ciphertext/salt می‌گذارد.

    پس از این تابع، چله دارای ciphertext و salt است و
    فیلدهای حساس آن خالی می‌شوند.
    """
    salt = os.urandom(SALT_SIZE)
    key = _derive_key(password, salt)
    f = Fernet(key)

    payload = {
        field: getattr(chelleh, field)
        for field in SENSITIVE_FIELDS
    }
    raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    token = f.encrypt(raw)

    chelleh.ciphertext = token.decode("ascii")
    chelleh.salt = base64.urlsafe_b64encode(salt).decode("ascii")
    chelleh.encrypted = True

    # پاک کردن داده‌های حساس از حافظه
    chelleh.name = ""
    chelleh.display_name = ""
    chelleh.task = ""
    chelleh.levels = []
    chelleh.daily_logs = {}
    chelleh.history = []


def decrypt_chelleh(chelleh, password: str) -> bool:
    """رمزگشایی محتوای چله با رمز عبور.

    Returns:
        True اگر رمز صحیح بود و داده‌ها در حافظه بارگذاری شدند.
        False اگر رمز اشتباه بود یا داده‌ها خراب بودند.
    """
    if not chelleh.encrypted or not chelleh.ciphertext:
        return False

    try:
        salt = base64.urlsafe_b64decode(chelleh.salt.encode("ascii"))
        key = _derive_key(password, salt)
        f = Fernet(key)
        raw = f.decrypt(chelleh.ciphertext.encode("ascii"))
        payload = json.loads(raw.decode("utf-8"))
    except (InvalidToken, ValueError, KeyError, json.JSONDecodeError):
        return False

    chelleh.name = payload.get("name", "")
    chelleh.display_name = payload.get("display_name", "")
    chelleh.task = payload.get("task", "")
    chelleh.levels = payload.get("levels", [])
    chelleh.daily_logs = payload.get("daily_logs", {})
    chelleh.history = payload.get("history", [])
    chelleh.encrypted = False

    return True


def change_password(chelleh, old_password: str, new_password: str) -> bool:
    """تغییر رمز چله قفل‌شده.

    ابتدا رمزگشایی و سپس با رمز جدید رمزنگاری می‌کند.
    چله بعد از این تابع دوباره قفل می‌شود.
    """
    if not decrypt_chelleh(chelleh, old_password):
        return False
    encrypt_chelleh(chelleh, new_password)
    return True