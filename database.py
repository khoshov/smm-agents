from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase

# Базовая модель для всех таблиц
class Base(DeclarativeBase):
    pass

# URL для SQLite в асинхронном режиме
DATABASE_URL = "sqlite+aiosqlite:///./telegram_bot.db"

# Создание асинхронного движка
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Логирование SQL запросов
    future=True
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Функция для получения сессии базы данных
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 