from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.core.config import settings
from app.core.exceptions import (
    SQLSessionError,
    UserExistedError,
)

engine = create_async_engine(settings.database_url, echo=True, future=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def unit_of_work():
    """
    Async context manager for handling database unit of work.

    Provides a transactional scope around a series of operations,
    commits the transaction if successful, and rolls back in case of errors.

    Catches and translates database exceptions into application-specific errors.

    :yields: AsyncSession
        An asynchronous SQLAlchemy session for database operations.
    :raises UserExistedError:
        Raised when a unique constraint violation (IntegrityError) occurs.
    :raises SQLSessionError:
        Raised on general SQLAlchemy errors during the transaction.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise UserExistedError(log_message=e)
        except SQLAlchemyError as e:
            await session.rollback()
            raise SQLSessionError(log_message=e)
        # except Exception as e:
        #     await session.rollback()
        #     raise GeneralSQLSessionError(log_message=e)


async def get_uow_session():
    """
    Dependency function to provide an async database session with automatic commit/rollback.

    Can be used with FastAPI's Depends on inject a transactional database session into path operations.

    :yields: AsyncSession
        An asynchronous SQLAlchemy session managed by the unit_of_work context.
    """
    async with unit_of_work() as session:
        yield session
