#!/usr/bin/env python3
"""
Бот для публикации одобренных новостей в канал
"""

import asyncio
import logging
from typing import Optional, List, Dict
from aiogram import Bot
from pydantic import SecretStr
from database import AsyncSessionLocal
from crud import NewsCRUD
from config import Settings

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PublisherBot:
    """Бот для публикации новостей в канал"""
    
    def __init__(self, bot_token: str, channel_id: str):
        """
        Инициализация бота издателя
        
        Args:
            bot_token: Токен бота для публикации
            channel_id: ID канала для публикации (например, "@channel_name" или "-1001234567890")
        """
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id
        self.is_running = False
        self.publish_task: Optional[asyncio.Task] = None
    
    async def format_news_message(self, news) -> str:
        """
        Форматирует новость для публикации в канал
        
        Args:
            news: Объект новости из базы данных
            
        Returns:
            str: Отформатированное сообщение
        """
        title = getattr(news, 'title', 'Без заголовка')
        content = getattr(news, 'content', 'Без содержания')
        url = getattr(news, 'url', None)
        
        # Форматируем сообщение
        message = f"📰 **{title}**\n\n{content}"
        
        # Добавляем источник, если есть
        if url:
            message += f"\n\n🔗 [Читать полностью]({url})"
        
        # Добавляем хештеги
        message += "\n\n#Новости #Информация"
        
        return message
    
    async def publish_news(self, news) -> bool:
        """
        Публикует одну новость в канал
        
        Args:
            news: Объект новости из базы данных
            
        Returns:
            bool: True если публикация успешна, False в противном случае
        """
        try:
            # Форматируем сообщение
            message = await self.format_news_message(news)
            
            # Публикуем в канал
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
            
            logger.info(f"Новость {getattr(news, 'id')} успешно опубликована в канал")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при публикации новости {getattr(news, 'id')}: {e}")
            return False
    
    async def publish_pending_news(self) -> List[Dict]:
        """
        Публикует все одобренные, но не опубликованные новости
        
        Returns:
            List[Dict]: Список результатов публикации
        """
        results = []
        
        async with AsyncSessionLocal() as session:
            # Получаем одобренные, но не опубликованные новости
            unpublished_news = await NewsCRUD.get_unpublished_approved_news(session)
            
            if not unpublished_news:
                logger.info("Нет новостей для публикации")
                return results
            
            logger.info(f"Найдено {len(unpublished_news)} новостей для публикации")
            
            for news in unpublished_news:
                news_id = getattr(news, 'id')
                title = getattr(news, 'title', 'Unknown')
                
                # Публикуем новость
                success = await self.publish_news(news)
                
                if success:
                    # Отмечаем как опубликованную в базе данных
                    await NewsCRUD.publish_news(session, news_id)
                    logger.info(f"Новость '{title}' (ID: {news_id}) опубликована и отмечена в БД")
                else:
                    logger.warning(f"Не удалось опубликовать новость '{title}' (ID: {news_id})")
                
                results.append({
                    "news_id": news_id,
                    "title": title,
                    "success": success
                })
                
                # Небольшая пауза между публикациями
                await asyncio.sleep(1)
        
        return results
    
    async def start_publishing_loop(self, interval_seconds: int = 300):
        """
        Запускает цикл публикации новостей
        
        Args:
            interval_seconds: Интервал между проверками новых новостей (по умолчанию 5 минут)
        """
        self.is_running = True
        logger.info(f"Запущен цикл публикации с интервалом {interval_seconds} секунд")
        
        while self.is_running:
            try:
                # Публикуем ожидающие новости
                results = await self.publish_pending_news()
                
                if results:
                    logger.info(f"Обработано {len(results)} новостей")
                    for result in results:
                        status = "✅" if result["success"] else "❌"
                        logger.info(f"{status} {result['title']} (ID: {result['news_id']})")
                
                # Ждем до следующей проверки
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Ошибка в цикле публикации: {e}")
                await asyncio.sleep(60)  # Ждем минуту при ошибке
    
    async def stop_publishing_loop(self):
        """Останавливает цикл публикации"""
        self.is_running = False
        logger.info("Цикл публикации остановлен")
    
    async def publish_single_news(self, news_id: int) -> bool:
        """
        Публикует одну конкретную новость
        
        Args:
            news_id: ID новости для публикации
            
        Returns:
            bool: True если публикация успешна
        """
        async with AsyncSessionLocal() as session:
            news = await NewsCRUD.get_news_by_id(session, news_id)
            
            if not news:
                logger.error(f"Новость с ID {news_id} не найдена")
                return False
            
            if not getattr(news, 'is_approved', False):
                logger.error(f"Новость {news_id} не одобрена для публикации")
                return False
            
            if getattr(news, 'is_published', False):
                logger.warning(f"Новость {news_id} уже опубликована")
                return False
            
            # Публикуем новость
            success = await self.publish_news(news)
            
            if success:
                # Отмечаем как опубликованную
                await NewsCRUD.publish_news(session, news_id)
                logger.info(f"Новость {news_id} успешно опубликована")
            
            return success
    
    async def get_publishing_stats(self) -> Dict:
        """
        Получает статистику публикаций
        
        Returns:
            Dict: Статистика публикаций
        """
        async with AsyncSessionLocal() as session:
            all_news = await NewsCRUD.get_all_news(session)
            approved_news = await NewsCRUD.get_approved_news(session)
            published_news = await NewsCRUD.get_published_news(session)
            unpublished_approved = await NewsCRUD.get_unpublished_approved_news(session)
            
            return {
                "total_news": len(all_news),
                "approved_news": len(approved_news),
                "published_news": len(published_news),
                "pending_publication": len(unpublished_approved)
            }

# Функция для создания экземпляра бота издателя
def create_publisher_bot(bot_token: str, channel_id: str) -> PublisherBot:
    """
    Создает экземпляр бота издателя
    
    Args:
        bot_token: Токен бота для публикации
        channel_id: ID канала для публикации
        
    Returns:
        PublisherBot: Экземпляр бота издателя
    """
    return PublisherBot(bot_token, channel_id)

# Пример использования
async def main():
    """Пример использования бота издателя"""
    # Здесь нужно указать реальные данные
    bot_token = "YOUR_PUBLISHER_BOT_TOKEN"
    channel_id = "@your_channel_name"  # или "-1001234567890"
    
    publisher = create_publisher_bot(bot_token, channel_id)
    
    try:
        # Запускаем цикл публикации
        await publisher.start_publishing_loop(interval_seconds=60)  # Проверяем каждую минуту
    except KeyboardInterrupt:
        logger.info("Получен сигнал завершения")
    finally:
        await publisher.stop_publishing_loop()

if __name__ == "__main__":
    asyncio.run(main()) 