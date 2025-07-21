import asyncio
from database import engine, Base
from models import User

async def init_db():
    """Инициализация базы данных - создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("База данных инициализирована успешно!")

async def drop_db():
    """Удаление всех таблиц из базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Все таблицы удалены!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "drop":
        asyncio.run(drop_db())
    else:
        asyncio.run(init_db()) 