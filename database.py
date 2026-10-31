from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///./cooking_book.db"

engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сессий
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


# Наш правильный генератор сессий для эндпоинтов (DI)
async def get_db():
    async with async_session() as session:
        yield session
