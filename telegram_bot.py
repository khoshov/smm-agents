from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
import logging
from config import Settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация асинхронного Telegram-бота

def get_telegram_bot(token: str) -> Bot:
    return Bot(token=token, session=AiohttpSession())

def get_moderator_bot(settings: Settings) -> Bot:
    return get_telegram_bot(settings.moderator_bot_token)

def get_publisher_bot(settings: Settings) -> Bot:
    return get_telegram_bot(settings.publisher_bot_token)

def get_telegram_dispatcher(bot: Bot) -> Dispatcher:
    return Dispatcher(bot=bot) 