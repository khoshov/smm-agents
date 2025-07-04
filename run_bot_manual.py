import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Bot token can be obtained via https://t.me/BotFather
# TOKEN = getenv("MODERATOR_BOT_TOKEN")
TOKEN = '7654803812:AAGDho-TAUiaA6QK6bN0-0hQ0ztpvpvECLU'

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()

message_text = "Эту новость надо проверить и принять решение о публикации"

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


# @dp.message()
# async def echo_handler(message: Message) -> None:
#     """
#     Handler will forward receive a message back to the sender

#     By default, message handler will handle all message types (like a text, photo, sticker etc.)
#     """
#     try:
#         # Send a copy of the received message
#         await message.send_copy(chat_id=message.chat.id)
#     except TypeError:
#         # But not all the types is supported to be copied so need to handle it
#         await message.answer("Nice try!")

@dp.message(Command("test"))
async def send_message(message: Message) -> None:
    try:
        await message.answer(chat_id=message.chat.id, text="Hello")
    except TypeError:
        await message.answer("Nice try!")

@dp.message(Command('post'))
async def send_message_with_buttons_manual(message: Message) -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await send_message_with_buttons(chat_id=message.chat.id, message_text=message_text, bot_instance=bot)


async def send_message_with_buttons(chat_id: int, message_text: str, bot_instance: Bot) -> None:
    """
    Отправляет сообщение с двумя кнопками: "опубликовать" и "отмена"
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="опубликовать", callback_data="publish_true"),
            InlineKeyboardButton(text="отмена", callback_data="publish_false")
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
        await callback.answer("Выбрано: опубликовать (True)")
        # Здесь можно добавить логику для обработки True
    elif callback.data == "publish_false":
        await callback.answer("Выбрано: отмена (False)")
        # Здесь можно добавить логику для обработки False
    
    # Убираем инлайн-клавиатуру после нажатия
    if callback.message:
        await callback.message.edit_reply_markup(reply_markup=None)



async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)
    


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
