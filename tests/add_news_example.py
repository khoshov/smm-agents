#!/usr/bin/env python3
"""
Пример скрипта для добавления новостей из внешнего источника
"""

import asyncio
import logging
from typing import List, Dict, Optional
from database import AsyncSessionLocal
from crud import NewsCRUD
from news_moderator_bot import NewsModeratorBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsCollector:
    """Класс для сбора новостей из внешних источников"""
    
    def __init__(self):
        self.bot = NewsModeratorBot()
    
    async def collect_news_from_external_source(self) -> List[Dict]:
        """
        Собирает новости из внешнего источника
        В реальном приложении здесь будет API запрос к новостному сервису
        
        Returns:
            List[Dict]: Список новостей с полями title, content, url
        """
        # Пример данных из внешнего источника
        sample_news = [
            {
                "title": "Важное событие в мире технологий",
                "content": "Сегодня произошло значимое событие в области искусственного интеллекта. Исследователи представили новую модель, которая превосходит все предыдущие достижения.",
                "url": "https://example.com/tech-news-1"
            },
            {
                "title": "Новости экономики",
                "content": "Центральный банк объявил о новых мерах по стабилизации экономики. Эксперты прогнозируют положительные изменения в ближайшие месяцы.",
                "url": "https://example.com/economy-news-1"
            },
            {
                "title": "Спортивные новости",
                "content": "Вчера состоялся захватывающий матч между ведущими командами лиги. Результат превзошел все ожидания болельщиков.",
                "url": "https://example.com/sports-news-1"
            }
        ]
        
        logger.info(f"Собрано {len(sample_news)} новостей из внешнего источника")
        return sample_news
    
    async def add_news_to_database(self, news_list: List[Dict]) -> List[int]:
        """
        Добавляет новости в базу данных
        
        Args:
            news_list: Список новостей для добавления
            
        Returns:
            List[int]: Список ID добавленных новостей
        """
        added_news_ids = []
        
        async with AsyncSessionLocal() as session:
            for news_data in news_list:
                try:
                    # Проверяем, не существует ли уже новость с таким URL
                    if news_data.get("url"):
                        existing_news = await NewsCRUD.get_news_by_url(session, news_data["url"])
                        if existing_news:
                            logger.warning(f"Новость с URL {news_data['url']} уже существует")
                            continue
                    
                    # Создаем новую новость
                    news = await NewsCRUD.create_news(
                        session=session,
                        title=news_data["title"],
                        content=news_data["content"],
                        url=news_data.get("url")
                    )
                    
                    added_news_ids.append(news.id)
                    logger.info(f"Добавлена новость: {news.title} (ID: {news.id})")
                    
                except Exception as e:
                    logger.error(f"Ошибка при добавлении новости '{news_data.get('title', 'Unknown')}': {e}")
        
        return added_news_ids
    
    async def send_news_for_moderation(self, news_ids: List[int]) -> List[Dict]:
        """
        Отправляет новости на модерацию
        
        Args:
            news_ids: Список ID новостей для модерации
            
        Returns:
            List[Dict]: Результаты модерации
        """
        moderation_results = []
        
        async with AsyncSessionLocal() as session:
            for news_id in news_ids:
                try:
                    # Получаем новость из базы данных
                    news = await NewsCRUD.get_news_by_id(session, news_id)
                    if not news:
                        logger.warning(f"Новость с ID {news_id} не найдена")
                        continue
                    
                    # Формируем текст для модерации
                    moderation_text = f"**{news.title}**\n\n{news.content}"
                    if getattr(news, 'url'):
                        moderation_text += f"\n\nИсточник: {getattr(news, 'url')}"
                    
                    # Отправляем на модерацию
                    logger.info(f"Отправка новости {news_id} на модерацию...")
                    result_news_id, is_approved = await self.bot.send_news_for_moderation(
                        str(news_id), moderation_text
                    )
                    
                    moderation_results.append({
                        "news_id": news_id,
                        "title": news.title,
                        "approved": is_approved,
                        "result_news_id": result_news_id
                    })
                    
                    logger.info(f"Новость {news_id} промодерирована: {'одобрена' if is_approved else 'отклонена'}")
                    
                except Exception as e:
                    logger.error(f"Ошибка при модерации новости {news_id}: {e}")
                    moderation_results.append({
                        "news_id": news_id,
                        "title": "Unknown",
                        "approved": False,
                        "error": str(e)
                    })
        
        return moderation_results
    
    async def process_news_collection(self):
        """
        Основной процесс сбора и обработки новостей
        """
        logger.info("Начинаем процесс сбора новостей...")
        
        try:
            # 1. Собираем новости из внешнего источника
            news_list = await self.collect_news_from_external_source()
            
            if not news_list:
                logger.warning("Новости не найдены")
                return
            
            # 2. Добавляем новости в базу данных
            added_news_ids = await self.add_news_to_database(news_list)
            
            if not added_news_ids:
                logger.warning("Новости не были добавлены в базу данных")
                return
            
            # 3. Отправляем новости на модерацию
            moderation_results = await self.send_news_for_moderation(added_news_ids)
            
            # 4. Выводим результаты
            logger.info("=== Результаты обработки новостей ===")
            for result in moderation_results:
                status = "✅ Одобрена" if result.get("approved") else "❌ Отклонена"
                logger.info(f"Новость {result['news_id']}: {result.get('title', 'Unknown')} - {status}")
            
        except Exception as e:
            logger.error(f"Ошибка в процессе сбора новостей: {e}")

async def main():
    """Основная функция"""
    collector = NewsCollector()
    
    # Запускаем бота в фоне
    collector.bot.polling_task = asyncio.create_task(collector.bot.start_polling())
    
    # Ждем немного для инициализации бота
    await asyncio.sleep(2)
    
    try:
        # Обрабатываем новости
        await collector.process_news_collection()
    finally:
        # Останавливаем бота
        await collector.bot.stop_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен Ctrl+C, завершаем работу...")
    except Exception as e:
        logger.error(f"Ошибка: {e}") 