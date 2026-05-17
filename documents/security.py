from cryptography.fernet import Fernet
import base64
import hashlib
from django.conf import settings


def get_key():
    # derive key from Django SECRET_KEY (stable)
    return base64.urlsafe_b64encode(
        hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    )


cipher = Fernet(get_key())


def encrypt_value(value):
    if not value or not isinstance(value, str):
        return value
    return cipher.encrypt(value.encode()).decode()


def decrypt_value(value):
    if not value or not isinstance(value, str):
        return value
    try:
        return cipher.decrypt(value.encode()).decode()
    except Exception:
        return value