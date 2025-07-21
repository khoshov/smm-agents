#!/usr/bin/env python3
"""
Пример конфигурационного файла для настройки токенов ботов
Скопируйте этот файл в config_local.py и заполните реальными данными
"""

from pydantic import SecretStr

# Конфигурация для бота модератора
MODERATOR_BOT_TOKEN = "YOUR_MODERATOR_BOT_TOKEN"  # Токен бота модератора

# Конфигурация для бота издателя
PUBLISHER_BOT_TOKEN = "YOUR_PUBLISHER_BOT_TOKEN"  # Токен бота издателя
CHANNEL_ID = "@your_channel_name"  # ID канала для публикации

# Примеры ID каналов:
# Публичный канал: "@channel_name"
# Приватный канал: "-1001234567890"
# Группа: "-1001234567890"

# Дополнительные настройки
PUBLISH_INTERVAL_SECONDS = 300  # Интервал проверки новых новостей для публикации (5 минут)
MODERATION_TIMEOUT_SECONDS = 1800  # Таймаут ожидания модерации (30 минут)

# Настройки логирования
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Настройки базы данных
DATABASE_URL = "sqlite+aiosqlite:///telegram_bot.db"

# Пример использования:
"""
# В вашем коде:
try:
    from config_local import *
except ImportError:
    print("Создайте файл config_local.py на основе config_example.py")
    exit(1)

# Инициализация бота модератора
moderator_bot = NewsModeratorBot(
    publisher_bot_token=PUBLISHER_BOT_TOKEN,
    channel_id=CHANNEL_ID
)

# Инициализация бота издателя
publisher_bot = PublisherBot(
    bot_token=PUBLISHER_BOT_TOKEN,
    channel_id=CHANNEL_ID
)
""" 