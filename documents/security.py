"""
📦 documents/security.py

Handles encryption & decryption of sensitive fields.

🧠 DESIGN:
- Uses Django SECRET_KEY to derive encryption key
- Field-level encryption (not full DB encryption)
- Safe fallback if decryption fails
"""

from cryptography.fernet import Fernet
import base64
import hashlib
from django.conf import settings


# =========================================================
# 🔐 KEY GENERATION
# =========================================================
def get_key():
    """
    Generates stable encryption key from Django SECRET_KEY
    """
    return base64.urlsafe_b64encode(
        hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    )


cipher = Fernet(get_key())


# =========================================================
# 🔒 ENCRYPTION
# =========================================================
def encrypt_value(value):
    """
    Encrypts string values safely
    """
    if not value or not isinstance(value, str):
        return value

    return cipher.encrypt(value.encode()).decode()


# =========================================================
# 🔓 DECRYPTION
# =========================================================
def decrypt_value(value):
    """
    Decrypts string values safely
    """
    if not value or not isinstance(value, str):
        return value

    try:
        return cipher.decrypt(value.encode()).decode()
    except Exception:
        return value