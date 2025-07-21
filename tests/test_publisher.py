#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности публикации новостей
"""

import asyncio
import logging
from database import AsyncSessionLocal
from crud import NewsCRUD, UserCRUD
from publisher_bot import PublisherBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_publisher_functionality():
    """Тестирование функциональности публикации"""
    logger.info("=== Тестирование функциональности публикации ===")
    
    # Тестовые данные (замените на реальные)
    test_bot_token = "8169955910:AAHyds5lwbLpafuBwl4jOdsY6Fd4l_4bSpU"  # Замените на реальный токен
    test_channel_id = "-1002704775312"  # Замените на реальный ID канала
    
    # Создаем тестового бота издателя
    publisher = PublisherBot(test_bot_token, test_channel_id)
    
    async with AsyncSessionLocal() as session:
        # 1. Создаем тестовую одобренную новость
        logger.info("1. Создание тестовой одобренной новости...")
        news = await NewsCRUD.create_news(
            session=session,
            title="Тестовая новость для публикации",
            content="Это тестовая новость, которая будет опубликована в канале для проверки функциональности системы публикации.",
            url="https://example.com/test-news"
        )
        
        # 2. Одобряем новость
        logger.info("2. Одобрение новости...")
        await NewsCRUD.moderate_news(
            session=session,
            news_id=getattr(news, 'id'),
            is_approved=True,
            moderator_id=12345,
            moderator_name="Test Moderator"
        )
        
        # 3. Проверяем статус новости
        logger.info("3. Проверка статуса новости...")
        updated_news = await NewsCRUD.get_news_by_id(session, getattr(news, 'id'))
        logger.info(f"Новость одобрена: {getattr(updated_news, 'is_approved')}")
        logger.info(f"Новость опубликована: {getattr(updated_news, 'is_published')}")
        
        # 4. Получаем статистику публикаций
        logger.info("4. Получение статистики публикаций...")
        stats = await publisher.get_publishing_stats()
        logger.info(f"Статистика: {stats}")
        
        # 5. Тестируем публикацию (только если указаны реальные данные)
        if test_bot_token != "YOUR_PUBLISHER_BOT_TOKEN" and test_channel_id != "@your_test_channel":
            logger.info("5. Тестирование публикации...")
            try:
                success = await publisher.publish_single_news(getattr(news, 'id'))
                if success:
                    logger.info("✅ Публикация успешна!")
                else:
                    logger.warning("❌ Публикация не удалась")
            except Exception as e:
                logger.error(f"Ошибка при публикации: {e}")
        else:
            logger.info("5. Пропуск теста публикации (не указаны реальные данные)")
        
        # 6. Проверяем список неопубликованных одобренных новостей
        logger.info("6. Проверка неопубликованных одобренных новостей...")
        unpublished_news = await NewsCRUD.get_unpublished_approved_news(session)
        logger.info(f"Найдено неопубликованных одобренных новостей: {len(unpublished_news)}")
        
        for news_item in unpublished_news:
            logger.info(f"  - {getattr(news_item, 'title')} (ID: {getattr(news_item, 'id')})")
        
        # 7. Тестируем массовую публикацию
        logger.info("7. Тестирование массовой публикации...")
        if test_bot_token != "YOUR_PUBLISHER_BOT_TOKEN" and test_channel_id != "@your_test_channel":
            try:
                results = await publisher.publish_pending_news()
                logger.info(f"Результаты массовой публикации: {len(results)} новостей обработано")
                for result in results:
                    status = "✅" if result["success"] else "❌"
                    logger.info(f"  {status} {result['title']}")
            except Exception as e:
                logger.error(f"Ошибка при массовой публикации: {e}")
        else:
            logger.info("7. Пропуск теста массовой публикации (не указаны реальные данные)")

async def test_news_workflow():
    """Тестирование полного workflow новостей"""
    logger.info("\n=== Тестирование полного workflow новостей ===")
    
    async with AsyncSessionLocal() as session:
        # 1. Создаем несколько новостей с разными статусами
        logger.info("1. Создание новостей с разными статусами...")
        
        # Новость 1: Ожидает модерации
        news1 = await NewsCRUD.create_news(
            session=session,
            title="Новость 1: Ожидает модерации",
            content="Эта новость ожидает модерации.",
            url="https://example.com/news1"
        )
        
        # Новость 2: Одобрена, но не опубликована
        news2 = await NewsCRUD.create_news(
            session=session,
            title="Новость 2: Одобрена, не опубликована",
            content="Эта новость одобрена, но еще не опубликована.",
            url="https://example.com/news2"
        )
        await NewsCRUD.moderate_news(
            session=session,
            news_id=getattr(news2, 'id'),
            is_approved=True,
            moderator_id=12345,
            moderator_name="Test Moderator"
        )
        
        # Новость 3: Отклонена
        news3 = await NewsCRUD.create_news(
            session=session,
            title="Новость 3: Отклонена",
            content="Эта новость была отклонена модератором.",
            url="https://example.com/news3"
        )
        await NewsCRUD.moderate_news(
            session=session,
            news_id=getattr(news3, 'id'),
            is_approved=False,
            moderator_id=12345,
            moderator_name="Test Moderator"
        )
        
        # Новость 4: Опубликована
        news4 = await NewsCRUD.create_news(
            session=session,
            title="Новость 4: Опубликована",
            content="Эта новость была одобрена и опубликована.",
            url="https://example.com/news4"
        )
        await NewsCRUD.moderate_news(
            session=session,
            news_id=getattr(news4, 'id'),
            is_approved=True,
            moderator_id=12345,
            moderator_name="Test Moderator"
        )
        await NewsCRUD.publish_news(session, getattr(news4, 'id'))
        
        # 2. Проверяем различные выборки новостей
        logger.info("2. Проверка различных выборок новостей...")
        
        all_news = await NewsCRUD.get_all_news(session)
        pending_news = await NewsCRUD.get_pending_news(session)
        approved_news = await NewsCRUD.get_approved_news(session)
        rejected_news = await NewsCRUD.get_rejected_news(session)
        published_news = await NewsCRUD.get_published_news(session)
        unpublished_approved = await NewsCRUD.get_unpublished_approved_news(session)
        
        logger.info(f"Всего новостей: {len(all_news)}")
        logger.info(f"Ожидают модерации: {len(pending_news)}")
        logger.info(f"Одобрено: {len(approved_news)}")
        logger.info(f"Отклонено: {len(rejected_news)}")
        logger.info(f"Опубликовано: {len(published_news)}")
        logger.info(f"Ожидают публикации: {len(unpublished_approved)}")
        
        # 3. Проверяем содержимое выборок
        logger.info("3. Проверка содержимого выборок...")
        
        logger.info("Ожидают модерации:")
        for news in pending_news:
            logger.info(f"  - {getattr(news, 'title')}")
        
        logger.info("Одобрено:")
        for news in approved_news:
            logger.info(f"  - {getattr(news, 'title')}")
        
        logger.info("Отклонено:")
        for news in rejected_news:
            logger.info(f"  - {getattr(news, 'title')}")
        
        logger.info("Опубликовано:")
        for news in published_news:
            logger.info(f"  - {getattr(news, 'title')}")
        
        logger.info("Ожидают публикации:")
        for news in unpublished_approved:
            logger.info(f"  - {getattr(news, 'title')}")

async def main():
    """Основная функция"""
    logger.info("Запуск тестирования публикации...")
    
    try:
        # Тестируем функциональность публикации
        await test_publisher_functionality()
        
        # Тестируем полный workflow
        await test_news_workflow()
        
        logger.info("\n=== Тестирование завершено успешно ===")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 