from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.config import settings
from app.core.security import verify_token
from app.core.database import get_db
from app.database.models import User


def get_api_key(x_api_key: str = Header(None, alias="X-API-Key")):
    """
    Validate the API key provided in the request header.
    
    Accepts header: X-API-Key: your-api-key
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Raises:
        HTTPException: If the API key is invalid or missing (403 Forbidden).
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key is required. Provide X-API-Key header."
        )
    
    if x_api_key.strip() != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return x_api_key


def get_token_from_header(authorization: str = Header(None, alias="Authorization")):
    """
    Extract JWT token from Authorization header
    
    Expects: Authorization: Bearer <token>
    
    Args:
        authorization: Authorization header value
        
    Returns:
        str: Extracted JWT token
        
    Raises:
        HTTPException: If authorization header is missing or malformed
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if it starts with "Bearer "
    parts = authorization.split()
    
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return parts[1]


def get_current_user_payload(token: str = Depends(get_token_from_header)):
    """
    Validate the JWT token and return the decoded payload.
    
    Args:
        token: JWT token extracted from Authorization header
        
    Returns:
        dict: The decoded payload from the JWT token
        
    Raises:
        HTTPException: If the token is invalid or expired (401 Unauthorized)
    """
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


def get_current_user(
    payload: dict = Depends(get_current_user_payload),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from database
    
    Args:
        payload: Decoded JWT token payload
        db: Database session
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: If user not found or inactive
    """
    username = payload.get("sub")
    
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure the current user is active
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Active user object
        
    Raises:
        HTTPException: If user is not active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure the current user is an admin
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Admin user object
        
    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def optional_authentication(
    authorization: str = Header(None, alias="Authorization")
) -> Optional[dict]:
    """
    Optional authentication - returns user payload if token provided, None otherwise
    Useful for endpoints that work both with and without authentication
    
    Args:
        authorization: Optional Authorization header
        
    Returns:
        Optional[dict]: User payload if authenticated, None otherwise
    """
    if not authorization:
        return None
    
    try:
        token = get_token_from_header(authorization)
        return verify_token(token)
    except:
        return None


