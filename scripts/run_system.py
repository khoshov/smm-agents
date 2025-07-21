#!/usr/bin/env python3
"""
Скрипт для запуска всей системы модерации и публикации новостей
"""

import asyncio
import logging
import signal
import sys
from typing import Optional

# Попытка импорта локальной конфигурации
try:
    from config_local import *
    print("✅ Загружена локальная конфигурация")
except ImportError:
    print("❌ Файл config_local.py не найден")
    print("📝 Создайте файл config_local.py на основе config_example.py")
    print("🔧 Заполните в нем реальные токены ботов и ID канала")
    sys.exit(1)

from news_moderator_bot import NewsModeratorBot
from publisher_bot import PublisherBot

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)

class NewsSystem:
    """Основной класс системы новостей"""
    
    def __init__(self):
        self.moderator_bot: Optional[NewsModeratorBot] = None
        self.publisher_bot: Optional[PublisherBot] = None
        self.publisher_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def initialize(self):
        """Инициализация системы"""
        logger.info("🚀 Инициализация системы новостей...")
        
        try:
            # Проверяем токены
            if MODERATOR_BOT_TOKEN == "YOUR_MODERATOR_BOT_TOKEN":
                raise ValueError("Не настроен токен бота модератора")
            
            if PUBLISHER_BOT_TOKEN == "YOUR_PUBLISHER_BOT_TOKEN":
                logger.warning("⚠️ Не настроен токен бота издателя - публикация отключена")
                publisher_enabled = False
            else:
                publisher_enabled = True
            
            if CHANNEL_ID == "@your_channel_name":
                logger.warning("⚠️ Не настроен ID канала - публикация отключена")
                publisher_enabled = False
            
            # Инициализируем бота модератора
            logger.info("📝 Инициализация бота модератора...")
            self.moderator_bot = NewsModeratorBot(
                publisher_bot_token=PUBLISHER_BOT_TOKEN if publisher_enabled else "",
                channel_id=CHANNEL_ID if publisher_enabled else ""
            )
            
            # Инициализируем бота издателя (если настроен)
            if publisher_enabled:
                logger.info("📤 Инициализация бота издателя...")
                self.publisher_bot = PublisherBot(
                    bot_token=PUBLISHER_BOT_TOKEN,
                    channel_id=CHANNEL_ID
                )
                
                # Запускаем цикл публикации в фоне
                self.publisher_task = asyncio.create_task(
                    self.publisher_bot.start_publishing_loop(PUBLISH_INTERVAL_SECONDS)
                )
                logger.info(f"🔄 Запущен цикл публикации с интервалом {PUBLISH_INTERVAL_SECONDS} секунд")
            
            logger.info("✅ Система инициализирована успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            raise
    
    async def start(self):
        """Запуск системы"""
        logger.info("▶️ Запуск системы...")
        self.is_running = True
        
        try:
            # Запускаем бота модератора
            if self.moderator_bot:
                await self.moderator_bot.start_polling()
        except Exception as e:
            logger.error(f"❌ Ошибка в работе системы: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Остановка системы"""
        logger.info("⏹️ Остановка системы...")
        self.is_running = False
        
        # Останавливаем бота издателя
        if self.publisher_bot:
            await self.publisher_bot.stop_publishing_loop()
        
        # Отменяем задачу публикации
        if self.publisher_task and not self.publisher_task.done():
            self.publisher_task.cancel()
            try:
                await self.publisher_task
            except asyncio.CancelledError:
                pass
        
        # Останавливаем бота модератора
        if self.moderator_bot:
            await self.moderator_bot.stop_polling()
        
        logger.info("✅ Система остановлена")

async def main():
    """Основная функция"""
    system = NewsSystem()
    
    # Настройка обработки сигналов
    def signal_handler():
        logger.info("📡 Получен сигнал завершения...")
        asyncio.create_task(system.stop())
    
    try:
        # Инициализируем систему
        await system.initialize()
        
        # Запускаем систему
        await system.start()
        
    except KeyboardInterrupt:
        logger.info("⌨️ Получен Ctrl+C")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
    finally:
        await system.stop()

if __name__ == "__main__":
    print("📰 Система модерации и публикации новостей")
    print("=" * 50)
    
    # Проверяем конфигурацию
    print(f"📝 Бот модератора: {'✅' if MODERATOR_BOT_TOKEN != 'YOUR_MODERATOR_BOT_TOKEN' else '❌'}")
    print(f"📤 Бот издателя: {'✅' if PUBLISHER_BOT_TOKEN != 'YOUR_PUBLISHER_BOT_TOKEN' else '❌'}")
    print(f"📢 Канал: {'✅' if CHANNEL_ID != '@your_channel_name' else '❌'}")
    print(f"⏱️ Интервал публикации: {PUBLISH_INTERVAL_SECONDS} сек")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Система завершена пользователем")
    except Exception as e:
        print(f"\n💥 Система завершена с ошибкой: {e}")
        sys.exit(1) 