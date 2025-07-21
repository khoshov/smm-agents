import asyncio
from database import AsyncSessionLocal
from crud import UserCRUD

async def setup_test_moderator():
    """Создание тестового модератора"""
    print("Создание тестового модератора...")
    
    # Замените на ваш Telegram ID
    test_telegram_id = 123456789  # Замените на ваш реальный Telegram ID
    
    async with AsyncSessionLocal() as session:
        try:
            # Проверяем, существует ли пользователь
            user = await UserCRUD.get_user_by_telegram_id(session, test_telegram_id)
            
            if user:
                # Обновляем статус модератора
                await UserCRUD.set_moderator_status(session, test_telegram_id, True)
                print(f"Пользователь {test_telegram_id} назначен модератором")
            else:
                # Создаем нового пользователя-модератора
                user = await UserCRUD.create_user(
                    session=session,
                    telegram_id=test_telegram_id,
                    username="test_moderator",
                    first_name="Test",
                    last_name="Moderator",
                    is_moderator=True
                )
                print(f"Создан новый модератор: {user}")
            
            # Проверяем список модераторов
            moderators = await UserCRUD.get_moderators(session)
            print(f"Всего модераторов в системе: {len(moderators)}")
            for mod in moderators:
                print(f"  - {mod.telegram_id} ({mod.username})")
                
        except Exception as e:
            print(f"Ошибка при создании модератора: {e}")

if __name__ == "__main__":
    print("ВАЖНО: Замените test_telegram_id на ваш реальный Telegram ID!")
    print("Чтобы узнать ваш Telegram ID, отправьте боту команду /start")
    print()
    
    asyncio.run(setup_test_moderator()) 