from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.security import create_token, hash_password, verify_password
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.database.models import User

router = APIRouter()

class AuthInput(BaseModel):
    username: str
    password: str

class RegisterInput(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: str


@router.post('/login')
def login(auth: AuthInput, db: Session = Depends(get_db)):
    """
    Login with username and password
    Returns JWT token if credentials are valid
    """
    # Find user in database
    user = db.query(User).filter(User.username == auth.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(auth.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Create JWT token
    token = create_token({'sub': user.username, 'user_id': user.id})
    
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }


@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(user_input: RegisterInput, db: Session = Depends(get_db)):
    """
    Register a new user account
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_input.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_input.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password strength (optional)
    if len(user_input.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )
    
    # Create new user
    hashed_pwd = hash_password(user_input.password)
    new_user = User(
        username=user_input.username,
        email=user_input.email,
        hashed_password=hashed_pwd,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        'message': 'User registered successfully',
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'created_at': new_user.created_at.isoformat()
        }
    }


@router.get('/me', response_model=UserResponse)
def get_current_user_info(
    user: User = Depends(get_current_user)
):
    """
    Get current logged-in user information
    Requires: Authorization header with Bearer token
    """
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat()
    }


@router.put('/me/update')
def update_user_profile(
    email: EmailStr = None,
    password: str = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile (email or password)
    Requires: Authorization header with Bearer token
    """
    updated_fields = []
    
    if email:
        # Check if email already taken by another user
        existing = db.query(User).filter(
            User.email == email,
            User.id != user.id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        
        user.email = email
        updated_fields.append('email')
    
    if password:
        if len(password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        user.hashed_password = hash_password(password)
        updated_fields.append('password')
    
    if updated_fields:
        db.commit()
        db.refresh(user)
    
    return {
        'message': 'Profile updated successfully',
        'updated_fields': updated_fields,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }


@router.post('/logout')
def logout(user: User = Depends(get_current_user)):
    """
    Logout endpoint (client should discard token)
    Requires: Authorization header with Bearer token
    """
    return {
        'message': f'User {user.username} logged out successfully',
        'note': 'Please discard the JWT token on client side'
    }