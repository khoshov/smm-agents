import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import Settings

logging.basicConfig(level=logging.INFO)

settings = Settings()

bot = Bot(token=settings.moderator_bot_token.get_secret_value())
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Привет! Я бот для тестирования.")

@dp.message(Command('test'))
async def test_command(message: Message):
    await message.answer("Тестовая команда")

async def send_message_with_buttons_manual(message_text: str) -> None:
    chat_id: int = 84761801
    await send_message_with_buttons(chat_id=chat_id, message_text=message_text, bot_instance=bot)

async def send_message_with_buttons(chat_id: int, message_text: str, bot_instance: Bot) -> None:
    """
    Отправляет сообщение с двумя кнопками: "опубликовать" и "отмена"
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="опубликовать", callback_data="publish_true"),
            InlineKeyboardButton(text="отклонить", callback_data="publish_false")
        ]
    ])
    
    await bot_instance.send_message(
        chat_id=chat_id,
        text=message_text,
        reply_markup=keyboard
    )

@dp.callback_query()
async def handle_button_click(callback: CallbackQuery) -> None:
    """
    Обработчик нажатий на инлайн-кнопки
    """
    if callback.data == "publish_true":
        await callback.answer("Новость опубликована")
        # Здесь можно добавить логику для обработки True
    elif callback.data == "publish_false":
        await callback.answer("Новость отклонена")
        # Здесь можно добавить логику для обработки False
    
    # Убираем инлайн-клавиатуру после нажатия
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())