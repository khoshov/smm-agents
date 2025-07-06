import asyncio
import logging
from typing import Dict, Optional, Tuple
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database import get_db, AsyncSessionLocal
from crud import UserCRUD
from config import Settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)

class NewsModeratorBot:
    def __init__(self):
        self.settings = Settings()
        self.bot = Bot(token=self.settings.moderator_bot_token)
        self.dp = Dispatcher()
        self.pending_news: Dict[str, Dict] = {}  # Хранение ожидающих модерации новостей
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и callback'ов"""
        
        @self.dp.message(Command("start"))
        async def start_command(message: types.Message):
            """Обработчик команды /start"""
            async with AsyncSessionLocal() as session:
                # Проверяем, существует ли пользователь
                user = await UserCRUD.get_user_by_telegram_id(session, message.from_user.id)
                if not user:
                    # Создаем нового пользователя
                    user = await UserCRUD.create_user(
                        session=session,
                        telegram_id=message.from_user.id,
                        username=message.from_user.username,
                        first_name=message.from_user.first_name,
                        last_name=message.from_user.last_name
                    )
                    await message.answer("Добро пожаловать! Вы зарегистрированы в системе модерации.")
                else:
                    await message.answer("С возвращением! Вы уже зарегистрированы в системе модерации.")
        
        @self.dp.message(Command("moderator"))
        async def set_moderator_command(message: types.Message):
            """Команда для установки статуса модератора (только для админов)"""
            # Здесь можно добавить проверку на админа
            async with AsyncSessionLocal() as session:
                await UserCRUD.set_moderator_status(session, message.from_user.id, True)
                await message.answer("Вам присвоены права модератора!")
        
        @self.dp.callback_query()
        async def handle_news_moderation(callback: CallbackQuery):
            """Обработчик нажатий на кнопки модерации"""
            if callback.data and callback.data.startswith("news_"):
                parts = callback.data.split("_")
                if len(parts) >= 3:
                    news_id = parts[1]
                    action = parts[2]  # approve или reject
                    
                    if news_id in self.pending_news:
                        news_data = self.pending_news[news_id]
                        is_approved = action == "approve"
                        
                        # Убираем клавиатуру
                        await callback.message.edit_reply_markup(reply_markup=None)
                        
                        # Отправляем результат
                        result_text = "✅ Новость одобрена" if is_approved else "❌ Новость отклонена"
                        await callback.message.edit_text(
                            f"{callback.message.text}\n\n{result_text} модератором {callback.from_user.full_name}"
                        )
                        
                        # Сохраняем результат
                        news_data["result"] = is_approved
                        news_data["moderator_id"] = callback.from_user.id
                        news_data["moderator_name"] = callback.from_user.full_name
                        
                        await callback.answer(f"Решение принято: {'одобрено' if is_approved else 'отклонено'}")
                    else:
                        await callback.answer("Новость уже неактуальна или не найдена")
    
    async def send_news_for_moderation(self, news_id: str, news_text: str) -> Tuple[str, bool]:
        """
        Отправляет новость на модерацию и возвращает результат
        
        Args:
            news_id: ID новости
            news_text: Текст новости для модерации
            
        Returns:
            Tuple[str, bool]: (news_id, approved)
        """
        # Создаем клавиатуру с кнопками
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
        self.pending_news[news_id] = {
            "text": news_text,
            "result": None,
            "moderator_id": None,
            "moderator_name": None
        }
        
        # Получаем всех модераторов
        async with AsyncSessionLocal() as session:
            moderators = await UserCRUD.get_moderators(session)
            
            if not moderators:
                raise Exception("Нет активных модераторов в системе")
            
            # Отправляем новость всем модераторам
            for moderator in moderators:
                try:
                    await self.bot.send_message(
                        chat_id=moderator.telegram_id,
                        text=f"📰 **Новость для модерации**\n\nID: `{news_id}`\n\n{news_text}",
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logging.error(f"Ошибка отправки новости модератору {moderator.telegram_id}: {e}")
        
        # Ждем решения модератора (максимум 30 минут)
        max_wait_time = 30 * 60  # 30 минут в секундах
        wait_time = 0
        check_interval = 5  # Проверяем каждые 5 секунд
        
        while wait_time < max_wait_time:
            if self.pending_news[news_id]["result"] is not None:
                result = self.pending_news[news_id]["result"]
                # Удаляем из ожидающих
                del self.pending_news[news_id]
                return news_id, result
            
            await asyncio.sleep(check_interval)
            wait_time += check_interval
        
        # Время истекло, считаем отклоненной
        if news_id in self.pending_news:
            del self.pending_news[news_id]
        return news_id, False
    
    async def start_polling(self):
        """Запуск бота"""
        await self.dp.start_polling(self.bot)

# Функция для внешнего использования
async def moderate_news(news_id: str, news_text: str) -> Tuple[str, bool]:
    """
    Функция для модерации новости
    
    Args:
        news_id: ID новости
        news_text: Текст новости
        
    Returns:
        Tuple[str, bool]: (news_id, approved)
    """
    bot_instance = NewsModeratorBot()
    return await bot_instance.send_news_for_moderation(news_id, news_text)

# Пример использования
async def main():
    """Пример использования бота"""
    bot = NewsModeratorBot()
    
    # Запускаем бота в фоне
    polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем немного для инициализации
    await asyncio.sleep(2)
    
    # Пример отправки новости на модерацию
    try:
        news_id, approved = await moderate_news(
            "news_001", 
            "Тестовая новость для проверки системы модерации"
        )
        print(f"Результат модерации: {news_id} - {'одобрено' if approved else 'отклонено'}")
    except Exception as e:
        print(f"Ошибка модерации: {e}")
    
    # Останавливаем бота
    polling_task.cancel()

if __name__ == "__main__":
    asyncio.run(main()) 