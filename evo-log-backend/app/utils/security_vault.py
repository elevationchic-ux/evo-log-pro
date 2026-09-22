import base64
import hashlib
from cryptography.fernet import Fernet
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# AES-256 Field Encryption for sensitive PII data
_FERNET_KEY = base64.urlsafe_b64encode(
    hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
)
_cipher = Fernet(_FERNET_KEY)

def encrypt_sensitive_field(plain_text: str) -> str:
    """Encrypt sensitive string field using AES-256 Fernet cipher."""
    if not plain_text:
        return plain_text
    try:
        return _cipher.encrypt(plain_text.encode('utf-8')).decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        return plain_text

def decrypt_sensitive_field(cipher_text: str) -> str:
    """Decrypt AES-256 cipher string."""
    if not cipher_text:
        return cipher_text
    try:
        return _cipher.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
    except Exception:
        # Return as-is if not encrypted
        return cipher_text
