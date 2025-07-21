import asyncio
from database import AsyncSessionLocal
from crud import UserCRUD

async def create_test_moderator(telegram_id: int, username: str = None, first_name: str = "Тестовый", last_name: str = "Модератор"):
    """Создает тестового модератора"""
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли пользователь
        user = await UserCRUD.get_user_by_telegram_id(session, telegram_id)
        
        if user:
            # Если пользователь существует, делаем его модератором
            await UserCRUD.set_moderator_status(session, telegram_id, True)
            print(f"Пользователь {telegram_id} назначен модератором")
        else:
            # Создаем нового пользователя-модератора
            user = await UserCRUD.create_user(
                session=session,
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                is_moderator=True
            )
            print(f"Создан новый модератор: {user.telegram_id}")

async def list_moderators():
    """Показывает всех модераторов"""
    async with AsyncSessionLocal() as session:
        moderators = await UserCRUD.get_moderators(session)
        print(f"Найдено модераторов: {len(moderators)}")
        for mod in moderators:
            print(f"- ID: {mod.id}, Telegram ID: {mod.telegram_id}, Имя: {mod.first_name} {mod.last_name}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Создаем модератора с указанным Telegram ID
        telegram_id = int(sys.argv[1])
        asyncio.run(create_test_moderator(telegram_id))
    else:
        # Показываем всех модераторов
        asyncio.run(list_moderators())
        print("\nДля создания модератора используйте:")
        print("python create_test_moderator.py <telegram_id>") 