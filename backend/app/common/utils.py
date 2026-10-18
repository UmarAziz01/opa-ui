import base64
import hashlib
import os
import secrets
import time
from datetime import datetime, timezone
from typing import Optional, Union

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError

# Inisialisasi PasswordHasher dengan parameter Argon2id default yang aman
_argon2_hasher = PasswordHasher(
    time_cost=3,        # Iterasi
    memory_cost=65536,  # 64 MB
    parallelism=4,      # Jumlah thread
    hash_len=32,        # Panjang hash
    salt_len=16,        # Panjang salt default (bytes)
)


# ── Epoch Time Helpers ────────────────────────────────────────────────────────

def current_epoch() -> int:
    """Mengembalikan waktu saat ini dalam format Unix epoch (detik, integer)."""
    return int(time.time())


def current_epoch_ms() -> int:
    """Mengembalikan waktu saat ini dalam Unix epoch milidetik (integer)."""
    return int(time.time() * 1000)


def datetime_to_epoch(dt: Optional[datetime]) -> Optional[int]:
    """Konversi objek datetime (timezone-aware atau naive) ke Unix epoch detik."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def epoch_to_datetime(epoch_sec: Optional[int]) -> Optional[datetime]:
    """Konversi Unix epoch detik ke objek datetime UTC."""
    if epoch_sec is None:
        return None
    return datetime.fromtimestamp(epoch_sec, tz=timezone.utc)


# ── Argon2 + Salt Cryptography Helpers ────────────────────────────────────────

def generate_salt(length: int = 16) -> str:
    """Generate cryptographically secure random salt (Base64 encoded string)."""
    return base64.b64encode(os.urandom(length)).decode("utf-8")


def hash_secret_argon2(plain_text: str, custom_salt: Optional[str] = None) -> str:
    """
    Melakukan hash plain text menggunakan Argon2id.
    Jika `custom_salt` diisi, teks akan digabungkan dengan salt sebelum di-hash.
    Secara default Argon2 internal juga membangkitkan salt cryptographically random unik.
    """
    text_to_hash = f"{custom_salt}:{plain_text}" if custom_salt else plain_text
    return _argon2_hasher.hash(text_to_hash)


def verify_secret_argon2(plain_text: str, hashed_value: str, custom_salt: Optional[str] = None) -> bool:
    """Verifikasi string plain text terhadap hash Argon2id."""
    text_to_verify = f"{custom_salt}:{plain_text}" if custom_salt else plain_text
    try:
        return _argon2_hasher.verify(hashed_value, text_to_verify)
    except (VerifyMismatchError, VerificationError):
        return False


def generate_secure_token(prefix: str = "opa_", nbytes: int = 32) -> tuple[str, str, str]:
    """
    Generate API / Service Token acak.
    Mengembalikan tuple: (raw_secret_token, token_prefix, sha256_hash).
    Hash SHA256 disimpan di DB untuk indexing cepat, atau di-hash via Argon2 untuk cold credential.
    """
    raw_random = secrets.token_urlsafe(nbytes)
    full_token = f"{prefix}{raw_random}"
    token_prefix = full_token[:12]
    token_hash = hashlib.sha256(full_token.encode("utf-8")).hexdigest()
    return full_token, token_prefix, token_hash