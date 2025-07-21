import asyncio
from news_moderator_bot import NewsModeratorBot

async def example_news_moderation():
    """Пример использования функции модерации новостей"""
    
    # Создаем и запускаем бота
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    bot.polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем немного для инициализации
    print("Инициализация бота...")
    await asyncio.sleep(3)
    
    try:
        # Пример 1: Модерация обычной новости
        print("Отправляем новость на модерацию...")
        news_id, approved = await bot.send_news_for_moderation(
            news_id="news_001",
            news_text="Важная новость: Запущен новый сервис для пользователей!"
        )
        print(f"Результат: {news_id} - {'✅ Одобрено' if approved else '❌ Отклонено'}")
        
        # Пример 2: Модерация другой новости
        print("\nОтправляем вторую новость...")
        news_id, approved = await bot.send_news_for_moderation(
            news_id="news_002", 
            news_text="Обновление системы: Добавлены новые функции безопасности"
        )
        print(f"Результат: {news_id} - {'✅ Одобрено' if approved else '❌ Отклонено'}")
        
    except Exception as e:
        print(f"Ошибка модерации: {e}")
    finally:
        # Останавливаем бота
        print("Завершение работы бота...")
        await bot.stop_polling()

async def example_with_timeout():
    """Пример с настройкой времени ожидания"""
    print("Запуск примера с настройкой времени ожидания...")
    
    # Создаем и запускаем бота
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    bot.polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем инициализации
    await asyncio.sleep(3)
    
    try:
        # Отправляем новость с коротким временем ожидания для тестирования
        print("Отправка новости с коротким временем ожидания...")
        
        # Временно изменяем время ожидания для тестирования
        original_max_wait_time = 600 * 60  # 10 часов
        test_wait_time = 60  # 1 минута для тестирования
        
        # Сохраняем оригинальное время и устанавливаем тестовое
        async def send_news_with_timeout(news_id: str, news_text: str, wait_time: int = 60) -> tuple[str, bool]:
            """Отправка новости с настраиваемым временем ожидания"""
            # Создаем клавиатуру с кнопками
            from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Опубликовать", 
                        callback_data=f"news_{news_id}_approve"
                    ),
                    InlineKeyboardButton(
                        text="❌ Отклонить", 
                        callback_data=f"news_{news_id}_reject"
                    )
                ]
            ])
            
            # Сохраняем информацию о новости
            bot.pending_news[news_id] = {
                "text": news_text,
                "result": None,
                "moderator_id": None,
                "moderator_name": None
            }
            
            # Получаем всех модераторов и отправляем новость
            from database import AsyncSessionLocal
            from crud import UserCRUD
            
            async with AsyncSessionLocal() as session:
                moderators = await UserCRUD.get_moderators(session)
                
                if not moderators:
                    raise Exception("Нет активных модераторов в системе")
                
                for moderator in moderators:
                    try:
                        chat_id = getattr(moderator, 'telegram_id')
                        await bot.bot.send_message(
                            chat_id=chat_id,
                            text=f"📰 **Новость для модерации**\n\nID: `{news_id}`\n\n{news_text}",
                            parse_mode="Markdown",
                            reply_markup=keyboard
                        )
                    except Exception as e:
                        print(f"Ошибка отправки новости модератору {getattr(moderator, 'telegram_id', 'unknown')}: {e}")
            
            # Ждем решения модератора с настраиваемым временем
            wait_time_elapsed = 0
            check_interval = 5
            
            while wait_time_elapsed < wait_time:
                if bot.pending_news[news_id]["result"] is not None:
                    result = bot.pending_news[news_id]["result"]
                    del bot.pending_news[news_id]
                    return news_id, result
                
                await asyncio.sleep(check_interval)
                wait_time_elapsed += check_interval
            
            # Время истекло
            if news_id in bot.pending_news:
                del bot.pending_news[news_id]
            return news_id, False
        
        # Тестируем с коротким временем ожидания
        news_id, approved = await send_news_with_timeout(
            news_id="test_timeout_001",
            news_text="Тестовая новость с коротким временем ожидания (1 минута)",
            wait_time=60
        )
        
        print(f"Результат: {news_id} - {'✅ Одобрено' if approved else '❌ Отклонено (время истекло)'}")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.stop_polling()

# Функция для интеграции с внешними системами
async def process_news_from_external_system(news_data: dict) -> dict:
    """
    Пример интеграции с внешней системой
    
    Args:
        news_data: Словарь с данными новости
        
    Returns:
        dict: Результат модерации
    """
    try:
        news_id = news_data.get("id", "unknown")
        news_text = news_data.get("text", "")
        
        if not news_text:
            return {"error": "Пустой текст новости"}
        
        # Создаем бота и отправляем на модерацию
        bot = NewsModeratorBot()
        bot.polling_task = asyncio.create_task(bot.start_polling())
        await asyncio.sleep(2)
        
        try:
            moderated_id, approved = await bot.send_news_for_moderation(news_id, news_text)
            return {
                "news_id": moderated_id,
                "approved": approved,
                "status": "success"
            }
        finally:
            await bot.stop_polling()
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }

async def run_with_graceful_shutdown(test_func):
    """Запуск с graceful shutdown"""
    try:
        await test_func()
    except KeyboardInterrupt:
        print("\n🛑 Получен Ctrl+C, завершаем работу...")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Выберите пример:")
    print("1. Базовый пример модерации")
    print("2. Пример с настраиваемым временем ожидания")
    
    choice = input("Введите номер (1 или 2): ").strip()
    
    if choice == "2":
        asyncio.run(run_with_graceful_shutdown(example_with_timeout))
    else:
        asyncio.run(run_with_graceful_shutdown(example_news_moderation)) 