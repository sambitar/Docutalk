import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import get_settings


def _aes_key() -> bytes:
    raw = get_settings().docutalk_secrets_key
    # Accept 64-char hex or derive 32 bytes from any string
    try:
        if len(raw) == 64:
            return bytes.fromhex(raw)
    except ValueError:
        pass
    return hashlib.sha256(raw.encode("utf-8")).digest()


def encrypt_secret(plaintext: str) -> bytes:
    key = _aes_key()
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    return nonce + ciphertext


def decrypt_secret(blob: bytes) -> str:
    key = _aes_key()
    nonce, ciphertext = blob[:12], blob[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")


def key_last4(api_key: str) -> str:
    cleaned = api_key.strip()
    return cleaned[-4:] if len(cleaned) >= 4 else cleaned


def encode_blob_b64(blob: bytes) -> str:
    return base64.b64encode(blob).decode("ascii")
