import asyncio
import logging
import signal
from typing import Dict, Optional, Tuple
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pydantic import SecretStr
from database import get_db, AsyncSessionLocal
from crud import UserCRUD, NewsCRUD
from config import Settings
from publisher_bot import PublisherBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)

class NewsModeratorBot:
    def __init__(self, publisher_bot_token: str = "", channel_id: str = ""):
        # Инициализируем настройки с значениями по умолчанию
        self.settings = Settings(
            google_api_key="",
            google_cse_id="",
            flowise_host="",
            flowise_id="",
            moderator_bot_token=SecretStr("7654803812:AAGiiNZn_hHFMriOheh4N5xUL2odFU3NRl0"),
            publisher_bot_token=SecretStr("8169955910:AAHyds5lwbLpafuBwl4jOdsY6Fd4l_4bSpU")
        )
        self.bot = Bot(token=self.settings.moderator_bot_token.get_secret_value())
        self.dp = Dispatcher()
        self.pending_news: Dict[str, Dict] = {}  # Хранение ожидающих модерации новостей
        self.polling_task: Optional[asyncio.Task] = None
        
        # Инициализируем бота издателя, если указаны токен и канал
        self.publisher_bot: Optional[PublisherBot] = None
        if publisher_bot_token and channel_id:
            self.publisher_bot = PublisherBot(publisher_bot_token, channel_id)
            logging.info("Бот издателя инициализирован")
        
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и callback'ов"""
        
        @self.dp.message(Command("start"))
        async def start_command(message: types.Message):
            """Обработчик команды /start"""
            if not message.from_user:
                return
                
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
            if not message.from_user:
                return
                
            # Здесь можно добавить проверку на админа
            async with AsyncSessionLocal() as session:
                await UserCRUD.set_moderator_status(session, message.from_user.id, True)
                await message.answer("Вам присвоены права модератора!")
        
        @self.dp.message(Command("stats"))
        async def stats_command(message: types.Message):
            """Команда для просмотра статистики новостей"""
            if not message.from_user:
                return
                
            async with AsyncSessionLocal() as session:
                # Получаем статистику
                all_news = await NewsCRUD.get_all_news(session)
                pending_news = await NewsCRUD.get_pending_news(session)
                approved_news = await NewsCRUD.get_approved_news(session)
                rejected_news = await NewsCRUD.get_rejected_news(session)
                published_news = await NewsCRUD.get_published_news(session)
                unpublished_approved = await NewsCRUD.get_unpublished_approved_news(session)
                
                stats_text = f"""
📊 **Статистика новостей**

📰 Всего новостей: {len(all_news)}
⏳ Ожидают модерации: {len(pending_news)}
✅ Одобрено: {len(approved_news)}
❌ Отклонено: {len(rejected_news)}
📤 Опубликовано: {len(published_news)}
🔄 Ожидают публикации: {len(unpublished_approved)}
                """
                
                await message.answer(stats_text, parse_mode="Markdown")
        
        @self.dp.message(Command("publish"))
        async def publish_command(message: types.Message):
            """Команда для ручной публикации одобренных новостей"""
            if not message.from_user:
                return
            
            if not self.publisher_bot:
                await message.answer("❌ Бот издателя не настроен")
                return
            
            await message.answer("🔄 Начинаю публикацию одобренных новостей...")
            
            try:
                results = await self.publisher_bot.publish_pending_news()
                
                if not results:
                    await message.answer("ℹ️ Нет новостей для публикации")
                    return
                
                # Формируем отчет о публикации
                success_count = sum(1 for r in results if r["success"])
                failed_count = len(results) - success_count
                
                report = f"📤 **Отчет о публикации**\n\n"
                report += f"✅ Успешно опубликовано: {success_count}\n"
                report += f"❌ Ошибок: {failed_count}\n\n"
                
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    report += f"{status} {result['title']}\n"
                
                await message.answer(report, parse_mode="Markdown")
                
            except Exception as e:
                logging.error(f"Ошибка при публикации: {e}")
                await message.answer(f"❌ Ошибка при публикации: {e}")
        
        @self.dp.callback_query()
        async def handle_news_moderation(callback: CallbackQuery):
            """Обработчик нажатий на кнопки модерации"""
            if not callback.data:
                return
                
            if callback.data.startswith("news_"):
                # Убираем префикс "news_" и разбираем остальное
                data_without_prefix = callback.data[5:]  # убираем "news_"
                
                # Ищем последнее подчеркивание для разделения ID и действия
                last_underscore_index = data_without_prefix.rfind("_")
                
                if last_underscore_index != -1:
                    news_id = data_without_prefix[:last_underscore_index]
                    action = data_without_prefix[last_underscore_index + 1:]
                    
                    if news_id in self.pending_news:
                        news_data = self.pending_news[news_id]
                        is_approved = action == "approve"
                        
                        # Сохраняем результат в базе данных
                        async with AsyncSessionLocal() as session:
                            try:
                                # Получаем новость из базы данных
                                db_news = await NewsCRUD.get_news_by_id(session, int(news_id))
                                if db_news:
                                    # Обновляем статус модерации
                                    await NewsCRUD.moderate_news(
                                        session=session,
                                        news_id=int(news_id),
                                        is_approved=is_approved,
                                        moderator_id=callback.from_user.id if callback.from_user else None,
                                        moderator_name=callback.from_user.full_name if callback.from_user else "Unknown"
                                    )
                                    logging.info(f"Новость {news_id} промодерирована: {'одобрена' if is_approved else 'отклонена'}")
                                    
                                    # Если новость одобрена и есть бот издателя, публикуем её
                                    if is_approved and self.publisher_bot:
                                        try:
                                            await self.publisher_bot.publish_single_news(int(news_id))
                                            logging.info(f"Новость {news_id} автоматически опубликована")
                                        except Exception as e:
                                            logging.error(f"Ошибка при автоматической публикации новости {news_id}: {e}")
                                else:
                                    logging.warning(f"Новость {news_id} не найдена в базе данных")
                            except Exception as e:
                                logging.error(f"Ошибка при сохранении результата модерации: {e}")
                        
                        # Сохраняем результат в памяти
                        news_data["result"] = is_approved
                        news_data["moderator_id"] = callback.from_user.id if callback.from_user else None
                        news_data["moderator_name"] = callback.from_user.full_name if callback.from_user else "Unknown"
                        
                        await callback.answer(f"Решение принято: {'одобрено' if is_approved else 'отклонено'}")
                    else:
                        await callback.answer("Новость уже неактуальна или не найдена")
                else:
                    logging.error(f"Неверный формат callback данных: {callback.data}")
                    await callback.answer("Ошибка в формате данных")
    
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
                    # Получаем значение telegram_id из объекта User
                    # SQLAlchemy возвращает значение, а не Column
                    chat_id = getattr(moderator, 'telegram_id')
                        
                    await self.bot.send_message(
                        chat_id=chat_id,
                        text=f"📰 **Новость для модерации**\n\nID: `{news_id}`\n\n{news_text}",
                        parse_mode="Markdown",
                        reply_markup=keyboard
                    )
                except Exception as e:
                    logging.error(f"Ошибка отправки новости модератору {getattr(moderator, 'telegram_id', 'unknown')}: {e}")
        
        # Ждем решения модератора (максимум 30 минут)
        max_wait_time = 600 * 60  # 30 минут в секундах
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
    
    async def stop_polling(self):
        """Остановка бота"""
        if self.polling_task and not self.polling_task.done():
            self.polling_task.cancel()
            try:
                await self.polling_task
            except asyncio.CancelledError:
                pass
        logging.info("Бот остановлен")

# Функция для внешнего использования
async def moderate_news(news_id: str, news_text: str, publisher_bot_token: str = "", channel_id: str = "") -> Tuple[str, bool]:
    """
    Функция для модерации новости
    
    Args:
        news_id: ID новости
        news_text: Текст новости
        publisher_bot_token: Токен бота издателя (опционально)
        channel_id: ID канала для публикации (опционально)
        
    Returns:
        Tuple[str, bool]: (news_id, approved)
    """
    bot_instance = NewsModeratorBot(publisher_bot_token, channel_id)
    return await bot_instance.send_news_for_moderation(news_id, news_text)

# Функция для запуска бота с правильной обработкой сигналов
async def run_bot_with_graceful_shutdown(publisher_bot_token: str = "", channel_id: str = ""):
    """Запуск бота с graceful shutdown"""
    bot = NewsModeratorBot(publisher_bot_token, channel_id)
    
    # Создаем задачу для polling
    bot.polling_task = asyncio.create_task(bot.start_polling())
    
    try:
        # Ждем завершения polling
        await bot.polling_task
    except asyncio.CancelledError:
        logging.info("Получен сигнал завершения")
    finally:
        # Останавливаем бота
        await bot.stop_polling()

# Пример использования
async def main():
    """Пример использования бота"""
    # Здесь можно указать токен бота издателя и ID канала
    publisher_bot_token = ""  # Добавьте токен бота издателя
    channel_id = ""  # Добавьте ID канала (например, "@your_channel")
    
    bot = NewsModeratorBot(publisher_bot_token, channel_id)
    
    # Запускаем бота в фоне
    bot.polling_task = asyncio.create_task(bot.start_polling())
    
    # Ждем немного для инициализации
    await asyncio.sleep(2)
    
    # Пример отправки новости на модерацию
    try:
        news_id, approved = await moderate_news(
            "news_001", 
            "Тестовая новость для проверки системы модерации",
            publisher_bot_token,
            channel_id
        )
        print(f"Результат модерации: {news_id} - {'одобрено' if approved else 'отклонено'}")
    except Exception as e:
        print(f"Ошибка модерации: {e}")
    finally:
        # Останавливаем бота
        await bot.stop_polling()

if __name__ == "__main__":
    # Настройка обработки сигналов
    def signal_handler():
        logging.info("Получен сигнал завершения, останавливаем бота...")
        # Отменяем все задачи
        for task in asyncio.all_tasks():
            if not task.done():
                task.cancel()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Получен Ctrl+C, завершаем работу...")
    except Exception as e:
        logging.error(f"Ошибка: {e}") 