import asyncio
import logging
import signal
from news_moderator_bot import NewsModeratorBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def simple_test():
    """Простой тест бота с уже запущенным процессом"""
    print("=== Простой тест бота модерации ===")
    
    # Создаем бота
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    print("Запуск бота...")
    bot.polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем инициализации
    print("Ожидание инициализации (3 секунды)...")
    await asyncio.sleep(3)
    
    try:
        # Тест 1: Отправка одной новости
        print("\n--- Тест 1: Отправка новости ---")
        news_id, approved = await bot.send_news_for_moderation(
            news_id="simple_test_001",
            news_text="Простая тестовая новость для проверки работы бота"
        )
        print(f"Результат: {news_id} - {'✅ Одобрено' if approved else '❌ Отклонено'}")
        
        # Тест 2: Отправка второй новости
        print("\n--- Тест 2: Отправка второй новости ---")
        news_id, approved = await bot.send_news_for_moderation(
            news_id="simple_test_002",
            news_text="Вторая тестовая новость с дополнительной информацией"
        )
        print(f"Результат: {news_id} - {'✅ Одобрено' if approved else '❌ Отклонено'}")
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Останавливаем бота
        print("\nОстановка бота...")
        await bot.stop_polling()
        print("Бот остановлен.")

async def quick_test():
    """Быстрый тест с коротким временем ожидания"""
    print("=== Быстрый тест (1 минута ожидания) ===")
    
    # Создаем бота
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    bot.polling_task = asyncio.create_task(bot.start_polling())
    await asyncio.sleep(3)
    
    try:
        # Временно изменяем время ожидания для быстрого тестирования
        original_max_wait_time = 600 * 60  # 10 часов
        
        # Создаем клавиатуру
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        news_id = "quick_test"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"news_{news_id}_approve"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"news_{news_id}_reject")
            ]
        ])
        
        # Сохраняем новость
        bot.pending_news[news_id] = {
            "text": "Быстрая тестовая новость",
            "result": None,
            "moderator_id": None,
            "moderator_name": None
        }
        
        # Отправляем модераторам
        from database import AsyncSessionLocal
        from crud import UserCRUD
        
        async with AsyncSessionLocal() as session:
            moderators = await UserCRUD.get_moderators(session)
            
            if not moderators:
                print("❌ Нет модераторов в системе!")
                return
            
            print(f"📤 Отправка новости {len(moderators)} модераторам...")
            
            for moderator in moderators:
                try:
                    chat_id = getattr(moderator, 'telegram_id')
                    await bot.bot.send_message(
                        chat_id=chat_id,
                        text="📰 **Быстрая тестовая новость**\n\nID: `quick_test`\n\nБыстрая тестовая новость для проверки работы бота",
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                    print(f"✅ Отправлено модератору {chat_id}")
                except Exception as e:
                    print(f"❌ Ошибка отправки модератору {getattr(moderator, 'telegram_id', 'unknown')}: {e}")
        
        # Ждем 1 минуту
        print("⏳ Ожидание решения модератора (1 минута)...")
        wait_time = 0
        max_wait = 60  # 1 минута
        check_interval = 5
        
        while wait_time < max_wait:
            if bot.pending_news[news_id]["result"] is not None:
                result = bot.pending_news[news_id]["result"]
                del bot.pending_news[news_id]
                print(f"✅ Результат получен: {'Одобрено' if result else 'Отклонено'}")
                return
            
            await asyncio.sleep(check_interval)
            wait_time += check_interval
            print(f"⏳ Прошло {wait_time} секунд...")
        
        # Время истекло
        if news_id in bot.pending_news:
            del bot.pending_news[news_id]
        print("⏰ Время ожидания истекло")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await bot.stop_polling()

async def run_with_graceful_shutdown(test_func):
    """Запуск теста с graceful shutdown"""
    try:
        await test_func()
    except KeyboardInterrupt:
        print("\n🛑 Получен Ctrl+C, завершаем работу...")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Выберите тест:")
    print("1. Простой тест (полное время ожидания)")
    print("2. Быстрый тест (1 минута)")
    
    choice = input("Введите номер (1 или 2): ").strip()
    
    if choice == "2":
        asyncio.run(run_with_graceful_shutdown(quick_test))
    else:
        asyncio.run(run_with_graceful_shutdown(simple_test)) 