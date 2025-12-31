from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
from typing import Dict, Optional


def create_token(data: dict, expire_minutes: int=30) -> str:
    """
    Create and return a signed JWT containing the given payload data,
    with an expiration time defined in minutes.
    """
    if expire_minutes <= 0:
        raise ValueError("expire_minutes must be a positive integer")
    to_encode = data.copy()
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    to_encode["exp"] = int(expire_at.timestamp())
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str) -> Optional[Dict[str, any]]:
    """
    Verify a JWT and return its payload if valid.

    The token signature, algorithm are validated.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None
