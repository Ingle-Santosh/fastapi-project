from fastapi import Header, HTTPException
from app.core.config import settings
from app.core.security import verify_token

def get_api_key(api_key: str = Header(...)):
    """
    Validate the API key provided in the request header.

    Raises:
        HTTPException: If the API key is invalid (403 Forbidden).
    """
    if api_key.strip() != settings.API_KEY:
        raise  HTTPException(status_code=403, detail="Invalid API key")
    

def get_current_user(token: str = Header(...)):
    """
    Validate the JWT token provided in the request header and return the user payload.

    Raises:
        HTTPException: If the token is invalid or expired (401 Unauthorized).

    Returns:
        dict: The decoded payload from the JWT token containing user information.
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code = 401, detail = 'Invalid JWt token')
    return payload