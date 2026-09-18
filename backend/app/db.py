"""The async engine, and one session per request."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    # A connection dropped by Postgres is replaced rather than handed out broken.
    pool_pre_ping=True,
)

SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Opened per request, closed at the end. Nothing is written until a handler commits."""
    async with SessionFactory() as session:
        yield session


# Write `session: SessionDep` in a handler, nothing more.
SessionDep = Annotated[AsyncSession, Depends(get_session)]
