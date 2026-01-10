"""Authentication endpoints."""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.core.security import verify_password, get_password_hash, create_access_token
from app.config import settings
from app.utils.logging import logger

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class Token(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserLogin(BaseModel):
    """User login request model."""
    username: str
    password: str


class UserCreate(BaseModel):
    """User creation request model."""
    username: str
    email: EmailStr
    password: str
    full_name: str = None


# TODO: Replace with actual database user model
# This is a placeholder for demonstration
MOCK_USERS = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin123"),  # In production, use secure default
        "full_name": "Administrator",
        "disabled": False,
    }
}


def get_user(username: str):
    """Get user by username (placeholder - replace with DB query)."""
    if username in MOCK_USERS:
        return MOCK_USERS[username]
    return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        
    Returns:
        User dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    from jose import JWTError, jwt
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(username=username)
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return JWT token.
    
    Args:
        form_data: OAuth2 password form with username and password
        
    Returns:
        Token with access token and expiration
        
    Raises:
        HTTPException: If credentials are invalid
    """
    user = get_user(form_data.username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["username"], "email": user["email"]},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login for user: {form_data.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60
    }


@router.get("/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user from token
        
    Returns:
        User information
    """
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user.get("full_name"),
        "disabled": current_user.get("disabled", False),
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user (placeholder - implement with proper validation).
    
    Args:
        user_data: User registration data
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username already exists
    """
    if get_user(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # TODO: Save to database instead of mock dictionary
    hashed_password = get_password_hash(user_data.password)
    new_user = {
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "full_name": user_data.full_name,
        "disabled": False,
    }
    
    logger.info(f"New user registered: {user_data.username}")
    
    return {
        "username": new_user["username"],
        "email": new_user["email"],
        "full_name": new_user["full_name"],
        "message": "User registered successfully"
    }

