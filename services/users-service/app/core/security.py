import os
import base64
import hashlib
import hmac

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt



from app.core.config import settings
#import bcrypt
#from passlib.context import CryptContext
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



"""def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)"""

# scrypt parameters — OWASP recommended minimums
# N=2^14, r=8, p=1 balances security and login latency (~100ms on modern hardware)
_N = 2 ** 14   # CPU/memory cost factor
_R = 8         # block size
_P = 1         # parallelisation factor
_SALT_BYTES = 16
_KEY_LEN = 32


def hash_password(password: str) -> str:
    """
    Hash a password using scrypt from the Python standard library.
    No external C dependencies — works on Windows, Linux, and macOS.
    Returns a storable string in the format:  scrypt$<b64_salt>$<b64_key>
    """
    salt = os.urandom(_SALT_BYTES)
    key = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_N,
        r=_R,
        p=_P,
        dklen=_KEY_LEN,
    )
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    key_b64 = base64.b64encode(key).decode("utf-8")
    return f"scrypt${salt_b64}${key_b64}"


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plain-text password against a stored scrypt hash.
    Uses hmac.compare_digest to prevent timing attacks.
    """
    try:
        _, salt_b64, key_b64 = hashed.split("$")
        salt = base64.b64decode(salt_b64)
        expected_key = base64.b64decode(key_b64)
        actual_key = hashlib.scrypt(
            plain.encode("utf-8"),
            salt=salt,
            n=_N,
            r=_R,
            p=_P,
            dklen=_KEY_LEN,
        )
        return hmac.compare_digest(actual_key, expected_key)
    except Exception:
        return False
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


