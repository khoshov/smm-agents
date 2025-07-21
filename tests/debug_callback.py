import asyncio
import logging
from news_moderator_bot import NewsModeratorBot

# Настройка логирования для отладки
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def debug_callback():
    """Отладка callback'ов"""
    print("=== Отладка callback'ов ===")
    
    # Создаем бота
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    print("Запуск бота...")
    bot.polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем инициализации
    await asyncio.sleep(3)
    
    try:
        # Тестируем с простым ID
        news_id = "debug_test"
        news_text = "Тестовая новость для отладки callback'ов"
        
        print(f"📤 Отправка новости с ID: {news_id}")
        print(f"📝 Текст: {news_text}")
        
        # Создаем клавиатуру
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
        
        print(f"🔗 Callback данные: news_{news_id}_approve и news_{news_id}_reject")
        
        # Сохраняем новость
        bot.pending_news[news_id] = {
            "text": news_text,
            "result": None,
            "moderator_id": None,
            "moderator_name": None
        }
        
        print(f"💾 Сохранена новость в pending_news: {list(bot.pending_news.keys())}")
        
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
                        text=f"📰 **Новость для модерации**\n\nID: `{news_id}`\n\n{news_text}",
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                    print(f"✅ Отправлено модератору {chat_id}")
                except Exception as e:
                    print(f"❌ Ошибка отправки модератору {getattr(moderator, 'telegram_id', 'unknown')}: {e}")
        
        # Ждем 2 минуты для тестирования
        print("⏳ Ожидание решения модератора (2 минуты)...")
        wait_time = 0
        max_wait = 120  # 2 минуты
        check_interval = 5
        
        while wait_time < max_wait:
            print(f"⏳ Проверка через {wait_time} секунд...")
            print(f"📋 Текущие pending_news: {list(bot.pending_news.keys())}")
            
            if news_id in bot.pending_news:
                result = bot.pending_news[news_id]["result"]
                if result is not None:
                    del bot.pending_news[news_id]
                    print(f"✅ Результат получен: {'Одобрено' if result else 'Отклонено'}")
                    return
                else:
                    print(f"⏳ Результат еще не получен: {result}")
            else:
                print(f"⚠️ Новость {news_id} не найдена в pending_news")
            
            await asyncio.sleep(check_interval)
            wait_time += check_interval
        
        # Время истекло
        if news_id in bot.pending_news:
            del bot.pending_news[news_id]
        print("⏰ Время ожидания истекло")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await bot.stop_polling()

async def run_with_graceful_shutdown():
    """Запуск с graceful shutdown"""
    try:
        await debug_callback()
    except KeyboardInterrupt:
        print("\n🛑 Получен Ctrl+C, завершаем отладку...")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_with_graceful_shutdown()) 