"""Password hashing (bcrypt) and JWT token utilities."""

from typing_extensions import deprecated
from datetime import datetime, timedelta, timezone
from typing import Any
import uuid
from jose import JWTError, jwt 
from passlib.context import CryptContext
from app.core.config import get_settings


settings = get_settings()
pwd_context = CryptContext(schemes=["bycript"], deprecated="auto")


# Passwords
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# JWT
def create_access_token(subject: str | uuid.UUID, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": str(subject), "exp": expire, "iat": datetime.now(timezone.utc)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGOEITHM)

def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHMS])
    except JWTError:
        return None
