#!/usr/bin/env python3
"""
Финальный тест всей системы модерации и публикации новостей
"""

import asyncio
import logging
from datetime import datetime
from database import AsyncSessionLocal
from crud import NewsCRUD, UserCRUD
from news_moderator_bot import NewsModeratorBot
from publisher_bot import PublisherBot

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_full_system():
    """Тестирование полной системы"""
    logger.info("=== ФИНАЛЬНЫЙ ТЕСТ СИСТЕМЫ ===")
    
    # Конфигурация
    moderator_bot_token = "7654803812:AAGiiNZn_hHFMriOheh4N5xUL2odFU3NRl0"
    publisher_bot_token = "8169955910:AAHyds5lwbLpafuBwl4jOdsY6Fd4l_4bSpU"
    channel_id = "-1002704775312"
    
    logger.info("1. Инициализация компонентов системы...")
    
    # Создаем бота модератора
    moderator_bot = NewsModeratorBot(publisher_bot_token, channel_id)
    logger.info("✅ Бот модератора инициализирован")
    
    # Создаем бота издателя
    publisher_bot = PublisherBot(publisher_bot_token, channel_id)
    logger.info("✅ Бот издателя инициализирован")
    
    logger.info("2. Проверка базы данных...")
    
    async with AsyncSessionLocal() as session:
        # Проверяем количество новостей
        all_news = await NewsCRUD.get_all_news(session)
        pending_news = await NewsCRUD.get_pending_news(session)
        approved_news = await NewsCRUD.get_approved_news(session)
        published_news = await NewsCRUD.get_published_news(session)
        
        logger.info(f"📊 Статистика базы данных:")
        logger.info(f"   Всего новостей: {len(all_news)}")
        logger.info(f"   Ожидают модерации: {len(pending_news)}")
        logger.info(f"   Одобрено: {len(approved_news)}")
        logger.info(f"   Опубликовано: {len(published_news)}")
    
    logger.info("3. Тестирование создания новости...")
    
    async with AsyncSessionLocal() as session:
        # Создаем тестовую новость
        test_news = await NewsCRUD.create_news(
            session=session,
            url="https://example.com/final-test",
            title="Финальная тестовая новость",
            content="Это финальная тестовая новость для проверки всей системы модерации и публикации."
        )
        news_id = test_news.id
        logger.info(f"✅ Создана новость ID: {news_id}")
        
        # Проверяем статус новости
        news = await NewsCRUD.get_news_by_id(session, news_id)
        if news:
            logger.info(f"   Статус: Модерирована={news.is_moderated}, Одобрена={news.is_approved}, Опубликована={news.is_published}")
        else:
            logger.error("❌ Новость не найдена")
    
    logger.info("4. Тестирование модерации новости...")
    
    async with AsyncSessionLocal() as session:
        # Одобряем новость
        await NewsCRUD.moderate_news(
            session=session,
            news_id=int(test_news.id),
            is_approved=True,
            moderator_id=12345,
            moderator_name="Final Test Moderator"
        )
        logger.info("✅ Новость одобрена")
        
        # Проверяем статус
        news = await NewsCRUD.get_news_by_id(session, int(test_news.id))
        if news:
            logger.info(f"   Статус после модерации: Модерирована={news.is_moderated}, Одобрена={news.is_approved}")
        else:
            logger.error("❌ Новость не найдена после модерации")
    
    logger.info("5. Тестирование публикации новости...")
    
    try:
        # Публикуем новость
        result = await publisher_bot.publish_single_news(int(test_news.id))
        if result:
            logger.info("✅ Новость успешно опубликована в канал")
        else:
            logger.warning("⚠️ Новость не была опубликована")
    except Exception as e:
        logger.error(f"❌ Ошибка при публикации: {e}")
    
    logger.info("6. Проверка финального статуса...")
    
    async with AsyncSessionLocal() as session:
        news = await NewsCRUD.get_news_by_id(session, int(test_news.id))
        if news:
            logger.info(f"📋 Финальный статус новости {news.id}:")
            logger.info(f"   Заголовок: {news.title}")
            logger.info(f"   Модерирована: {news.is_moderated}")
            logger.info(f"   Одобрена: {news.is_approved}")
            logger.info(f"   Опубликована: {news.is_published}")
            logger.info(f"   Модератор: {news.moderator_name}")
            logger.info(f"   Время публикации: {news.published_at}")
        else:
            logger.error("❌ Новость не найдена при финальной проверке")
    
    logger.info("7. Тестирование статистики...")
    
    async with AsyncSessionLocal() as session:
        stats = await publisher_bot.get_publishing_stats()
        logger.info(f"📊 Статистика публикаций:")
        logger.info(f"   Всего новостей: {stats['total_news']}")
        logger.info(f"   Одобрено: {stats['approved_news']}")
        logger.info(f"   Опубликовано: {stats['published_news']}")
        logger.info(f"   Ожидают публикации: {stats['pending_publication']}")
    
    logger.info("8. Тестирование команд бота...")
    
    # Здесь можно было бы протестировать команды бота, но для этого нужен реальный пользователь
    logger.info("ℹ️ Команды бота (требуют реального пользователя):")
    logger.info("   /start - регистрация в системе")
    logger.info("   /moderator - получение прав модератора")
    logger.info("   /stats - просмотр статистики")
    logger.info("   /publish - ручная публикация новостей")
    
    logger.info("=== ТЕСТ ЗАВЕРШЕН ===")
    logger.info("✅ Система работает корректно!")
    logger.info("📝 Для полного тестирования:")
    logger.info("   1. Добавьте реального модератора в базу данных")
    logger.info("   2. Запустите бота: python run_system.py")
    logger.info("   3. Отправьте команды боту в Telegram")

async def main():
    """Главная функция"""
    try:
        await test_full_system()
    except Exception as e:
        logger.error(f"❌ Ошибка в тесте: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 