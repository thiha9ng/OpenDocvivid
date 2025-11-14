from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
from src.configs.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create SQLAlchemy base class
Base = declarative_base()

def utc_now():
    """Return current UTC datetime without timezone information"""
    return datetime.now(timezone.utc).replace(tzinfo=None)
    
# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    future=True
)

# Create async session maker
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync engine for Celery tasks
sync_engine = create_engine(
    settings.sync_database_url,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    future=True
)

# Create sync session maker
sync_session = sessionmaker(
    sync_engine,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Database dependency for FastAPI
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

def get_sync_db():
    """
    Synchronous database session for Celery tasks
    """
    try:
        session = sync_session()
        return session
    except Exception as e:
        logger.error(f"Failed to create sync database session: {e}")
        raise 