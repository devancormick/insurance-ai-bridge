#!/usr/bin/env python3
"""Create admin user script."""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import get_password_hash
from app.config import settings
from app.utils.logging import logger
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.base import Base
from app.models.user import User
import uuid


async def create_admin_user(
    username: str = "admin",
    email: str = "admin@example.com",
    password: str = "admin123",
    full_name: str = "Administrator"
):
    """Create an admin user in the database."""
    # Create database engine
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug
    )
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Check if admin user already exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.username == username)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                logger.warning(f"User '{username}' already exists. Updating password...")
                existing_user.hashed_password = get_password_hash(password)
                existing_user.is_superuser = True
                existing_user.disabled = False
                await session.commit()
                logger.info(f"Admin user '{username}' updated successfully")
                return existing_user
            
            # Create new admin user
            admin_user = User(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                disabled=False,
                is_superuser=True
            )
            
            session.add(admin_user)
            await session.commit()
            
            logger.info(f"Admin user '{username}' created successfully")
            logger.info(f"Email: {email}")
            logger.warning(f"Password: {password} (please change this in production!)")
            
            return admin_user
            
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--email", default="admin@example.com", help="Admin email")
    parser.add_argument("--password", default="admin123", help="Admin password")
    parser.add_argument("--full-name", default="Administrator", help="Admin full name")
    
    args = parser.parse_args()
    
    try:
        await create_admin_user(
            username=args.username,
            email=args.email,
            password=args.password,
            full_name=args.full_name
        )
        print(f"\n✓ Admin user '{args.username}' created successfully!")
        print(f"  Email: {args.email}")
        print(f"  Password: {args.password}")
        print("\n⚠️  IMPORTANT: Change the default password in production!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error creating admin user: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

