from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.core.security import create_token, hash_password, verify_password
from app.core.database import get_db
from app.database.models import User
from app.core.dependencies import get_current_user


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
    created_at: str

@router.post('/login/demo')
def demo_login(auth: AuthInput):
    """Demo login (no database) - For testing only"""
    if (auth.username == 'admin') and (auth.password == 'admin'):
        token = create_token({'sub': auth.username})
        return {'access_token': token, 'token_type': 'bearer'}
    return {'error': 'Invalid Credentials'}


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
            'username': user.username,
            'email': user.email
        }
    }


@router.post('/register', status_code=status.HTTP_201_CREATED)
def register(user_input: RegisterInput, db: Session = Depends(get_db)):
    """
    Register a new user
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


@router.get('/me')
def get_current_user_info(user = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get current logged-in user information
    """
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        'id': db_user.id,
        'username': db_user.username,
        'email': db_user.email,
        'is_active': db_user.is_active,
        'is_admin': db_user.is_admin,
        'created_at': db_user.created_at.isoformat()
    }

