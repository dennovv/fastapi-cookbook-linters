from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

DATABASE_URL = "sqlite+aiosqlite:///./cooking_book.db"

engine = create_async_engine(DATABASE_URL, echo=True)

# Используем строго типизированный async_sessionmaker для SQLAlchemy 2.0
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


# Явно указываем тип генератора для mypy
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
