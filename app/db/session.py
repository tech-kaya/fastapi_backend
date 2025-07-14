from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from app.core.config import settings
import asyncio
import logging


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    # Use NullPool for async engines to avoid connection pool issues
    poolclass=NullPool,
    # Connection arguments for asyncpg - optimized for long-running operations
    connect_args={
        "command_timeout": 300,  # 5 minutes command timeout
        "server_settings": {
            "application_name": "fastapi_form_automation",
            "statement_timeout": "300000",  # 5 minutes statement timeout
            "idle_in_transaction_session_timeout": "600000",  # 10 minutes idle timeout
        }
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    """Get database session with proper error handling"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def get_db_with_retry(max_retries: int = 3):
    """Get database session with retry logic for long-running operations"""
    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as session:
                yield session
                return
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            # Log the retry attempt
            logging.warning(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            await asyncio.sleep(1)  # Wait before retry 