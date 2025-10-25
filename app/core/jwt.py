import time
import jwt
from app.config import settings


def create_access_token(subject: str, expires_in: int = 3600) -> str:
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + expires_in}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])