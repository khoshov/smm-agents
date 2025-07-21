import asyncio
import logging
from news_moderator_bot import NewsModeratorBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def test_bot():
    """Тестирование бота"""
    print("Запуск тестирования бота...")
    
    # Создаем бота
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем инициализации
    print("Ожидание инициализации бота...")
    await asyncio.sleep(3)
    
    try:
        # Тестируем отправку новости
        print("Отправка новости на модерацию...")
        news_id, approved = await bot.send_news_for_moderation(
            news_id="test_001",
            news_text="Тестовая новость: Проверка работы системы модерации"
        )
        
        print(f"Результат модерации: {news_id} - {'✅ Одобрено' if approved else '❌ Отклонено'}")
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        
    finally:
        # Останавливаем бота
        print("Остановка бота...")
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass

async def test_multiple_news():
    """Тестирование отправки нескольких новостей"""
    print("Запуск тестирования нескольких новостей...")
    
    # Создаем бота
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем инициализации
    print("Ожидание инициализации бота...")
    await asyncio.sleep(3)
    
    try:
        # Тестируем отправку нескольких новостей
        news_list = [
            ("test_001", "Первая тестовая новость: Важные обновления системы"),
            ("test_002", "Вторая тестовая новость: Новые функции безопасности"),
            ("test_003", "Третья тестовая новость: Улучшения производительности")
        ]
        
        for news_id, news_text in news_list:
            print(f"\nОтправка новости {news_id}...")
            try:
                result_id, approved = await bot.send_news_for_moderation(
                    news_id=news_id,
                    news_text=news_text
                )
                print(f"Результат: {result_id} - {'✅ Одобрено' if approved else '❌ Отклонено'}")
            except Exception as e:
                print(f"Ошибка при отправке новости {news_id}: {e}")
            
            # Небольшая пауза между новостями
            await asyncio.sleep(2)
        
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")
        
    finally:
        # Останавливаем бота
        print("\nОстановка бота...")
        polling_task.cancel()
        try:
            await polling_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    # Выберите один из вариантов тестирования
    print("Выберите вариант тестирования:")
    print("1. Одна новость")
    print("2. Несколько новостей")
    
    choice = input("Введите номер (1 или 2): ").strip()
    
    if choice == "2":
        asyncio.run(test_multiple_news())
    else:
        asyncio.run(test_bot()) 