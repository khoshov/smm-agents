import asyncio
import logging
from news_moderator_bot import NewsModeratorBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def test_ctrl_c():
    """Тест обработки Ctrl+C"""
    print("=== Тест обработки Ctrl+C ===")
    print("Запуск бота...")
    print("Нажмите Ctrl+C для остановки")
    
    # Создаем бота
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    bot.polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем инициализации
    await asyncio.sleep(3)
    print("✅ Бот запущен и готов к работе")
    
    try:
        # Бесконечный цикл для демонстрации
        counter = 0
        while True:
            await asyncio.sleep(5)
            counter += 1
            print(f"⏰ Прошло {counter * 5} секунд... (Ctrl+C для остановки)")
            
    except KeyboardInterrupt:
        print("\n🛑 Получен Ctrl+C!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        print("🔄 Остановка бота...")
        await bot.stop_polling()
        print("✅ Бот успешно остановлен")

if __name__ == "__main__":
    asyncio.run(test_ctrl_c()) 