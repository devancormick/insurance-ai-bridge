#!/usr/bin/env python3
"""Seed database with development data."""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import uuid

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.claim import Claim
from app.models.policy import Policy
from app.models.member import Member
from app.models.user import User
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.utils.logging import logger


async def seed_database():
    """Seed database with development data."""
    # Create database engine
    engine = create_async_engine(settings.database_url, echo=settings.debug)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # Create test users
            from sqlalchemy import select
            
            # Check if data already exists
            result = await session.execute(select(User).where(User.username == "testuser"))
            if result.scalar_one_or_none():
                logger.info("Database already seeded, skipping...")
                return
            
            # Create test users
            users = [
                User(
                    id=str(uuid.uuid4()),
                    username="testuser",
                    email="test@example.com",
                    hashed_password=get_password_hash("test123"),
                    full_name="Test User",
                    disabled=False,
                    is_superuser=False
                ),
                User(
                    id=str(uuid.uuid4()),
                    username="admin",
                    email="admin@example.com",
                    hashed_password=get_password_hash("admin123"),
                    full_name="Administrator",
                    disabled=False,
                    is_superuser=True
                )
            ]
            
            for user in users:
                session.add(user)
            
            # Create test members
            members = [
                Member(
                    id=f"MEM-{10000 + i}",
                    first_name="John",
                    last_name="Doe",
                    date_of_birth=datetime(1980, 1, 1),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ) for i in range(5)
            ]
            
            for member in members:
                session.add(member)
            
            # Create test policies
            policies = [
                Policy(
                    id=f"POL-{20000 + i}",
                    policy_number=f"POL-{20000 + i}",
                    member_id=members[i % len(members)].id,
                    effective_date=datetime.utcnow() - timedelta(days=365),
                    expiration_date=datetime.utcnow() + timedelta(days=365),
                    coverage_type="medical",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ) for i in range(5)
            ]
            
            for policy in policies:
                session.add(policy)
            
            # Create test claims
            claims = [
                Claim(
                    id=f"CLM-{30000 + i}",
                    claim_number=f"CLM-{30000 + i}",
                    member_id=members[i % len(members)].id,
                    policy_id=policies[i % len(policies)].id,
                    claim_amount=1000.0 + (i * 100),
                    claim_date=datetime.utcnow() - timedelta(days=i * 10),
                    status="pending",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ) for i in range(10)
            ]
            
            for claim in claims:
                session.add(claim)
            
            await session.commit()
            
            logger.info("✓ Database seeded successfully!")
            logger.info(f"  - {len(users)} users created")
            logger.info(f"  - {len(members)} members created")
            logger.info(f"  - {len(policies)} policies created")
            logger.info(f"  - {len(claims)} claims created")
            
        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


async def main():
    """Main function."""
    try:
        await seed_database()
        print("\n✓ Database seeded successfully!")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error seeding database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

