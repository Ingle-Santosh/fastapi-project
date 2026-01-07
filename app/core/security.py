from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
from app.core.config import settings
#from passlib.context import CryptContext
from typing import Dict, Optional
from argon2 import PasswordHasher


# Password hashing context
#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = PasswordHasher()

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

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False