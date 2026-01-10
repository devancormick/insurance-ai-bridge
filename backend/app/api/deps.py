"""API dependencies."""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import settings
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.utils.logging import logger

# Lazy initialization of engine (created on first use)
_engine: Optional[any] = None
_AsyncSessionLocal: Optional[any] = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_engine():
    """Get or create the async database engine."""
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            echo=settings.debug,
        )
    return _engine


def get_session_maker():
    """Get or create the async session factory."""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = get_engine()
        _AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    AsyncSessionLocal = get_session_maker()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[dict]:
    """
    Get current user (optional authentication).
    
    Returns None if not authenticated instead of raising error.
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
        
        # Load from database
        from app.models.user import User
        from sqlalchemy import select
        
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user_orm = result.scalar_one_or_none()
        
        if user_orm:
            return {
                "id": user_orm.id,
                "username": user_orm.username,
                "email": user_orm.email,
                "full_name": user_orm.full_name,
                "disabled": user_orm.disabled,
                "is_superuser": user_orm.is_superuser
            }
        
        return None
        
    except JWTError:
        return None


async def get_current_user_required(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Get current user (required authentication).
    
    Raises AuthenticationError if not authenticated.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise AuthenticationError("Could not validate credentials")
        
        # Load from database
        from app.models.user import User
        from sqlalchemy import select
        
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user_orm = result.scalar_one_or_none()
        
        if user_orm is None:
            raise AuthenticationError("User not found")
        
        if user_orm.disabled:
            raise AuthorizationError("User account is disabled")
        
        return {
            "id": user_orm.id,
            "username": user_orm.username,
            "email": user_orm.email,
            "full_name": user_orm.full_name,
            "disabled": user_orm.disabled,
            "is_superuser": user_orm.is_superuser
        }
        
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise AuthenticationError("Could not validate credentials")


def require_permission(permission: str):
    """
    Dependency factory to require specific permission.
    
    Args:
        permission: Required permission name
        
    Returns:
        Dependency function
    """
    async def permission_checker(user: dict = Depends(get_current_user_required)):
        user_permissions = user.get("permissions", [])
        if permission not in user_permissions:
            raise AuthorizationError(f"Permission '{permission}' required")
        return user
    
    return permission_checker


def require_role(role: str):
    """
    Dependency factory to require specific role.
    
    Args:
        role: Required role name
        
    Returns:
        Dependency function
    """
    async def role_checker(user: dict = Depends(get_current_user_required)):
        user_role = user.get("role")
        if user_role != role and not user.get("is_superuser", False):
            raise AuthorizationError(f"Role '{role}' required")
        return user
    
    return role_checker
