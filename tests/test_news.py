#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы с новостями
"""

import asyncio
import logging
from database import AsyncSessionLocal
from crud import NewsCRUD, UserCRUD

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_news_operations():
    """Тестирование операций с новостями"""
    logger.info("=== Тестирование операций с новостями ===")
    
    async with AsyncSessionLocal() as session:
        # 1. Создаем тестовую новость
        logger.info("1. Создание тестовой новости...")
        news = await NewsCRUD.create_news(
            session=session,
            title="Тестовая новость",
            content="Это тестовая новость для проверки функциональности",
            url="https://test.com/news-1"
        )
        logger.info(f"Создана новость: ID={news.id}, Заголовок='{news.title}'")
        
        # 2. Получаем новость по ID
        logger.info("2. Получение новости по ID...")
        retrieved_news = await NewsCRUD.get_news_by_id(session, getattr(news, 'id'))
        if retrieved_news:
            logger.info(f"Получена новость: ID={retrieved_news.id}, Заголовок='{retrieved_news.title}'")
        else:
            logger.error("Новость не найдена!")
        
        # 3. Получаем новость по URL
        logger.info("3. Получение новости по URL...")
        url_news = await NewsCRUD.get_news_by_url(session, "https://test.com/news-1")
        if url_news:
            logger.info(f"Найдена новость по URL: ID={url_news.id}")
        else:
            logger.error("Новость по URL не найдена!")
        
        # 4. Создаем еще несколько новостей
        logger.info("4. Создание дополнительных новостей...")
        news2 = await NewsCRUD.create_news(
            session=session,
            title="Вторая новость",
            content="Содержание второй новости",
            url="https://test.com/news-2"
        )
        
        news3 = await NewsCRUD.create_news(
            session=session,
            title="Третья новость",
            content="Содержание третьей новости",
            url="https://test.com/news-3"
        )
        
        # 5. Получаем все новости
        logger.info("5. Получение всех новостей...")
        all_news = await NewsCRUD.get_all_news(session)
        logger.info(f"Всего новостей в базе: {len(all_news)}")
        
        # 6. Получаем новости, ожидающие модерации
        logger.info("6. Получение новостей, ожидающих модерации...")
        pending_news = await NewsCRUD.get_pending_news(session)
        logger.info(f"Новостей, ожидающих модерации: {len(pending_news)}")
        
        # 7. Модерируем одну из новостей
        logger.info("7. Модерация новости...")
        moderated_news = await NewsCRUD.moderate_news(
            session=session,
            news_id=getattr(news, 'id'),
            is_approved=True,
            moderator_id=12345,
            moderator_name="Test Moderator"
        )
        if moderated_news:
            logger.info(f"Новость {getattr(moderated_news, 'id')} промодерирована: одобрена")
        
        # 8. Отклоняем другую новость
        logger.info("8. Отклонение новости...")
        rejected_news = await NewsCRUD.moderate_news(
            session=session,
            news_id=getattr(news2, 'id'),
            is_approved=False,
            moderator_id=12345,
            moderator_name="Test Moderator"
        )
        if rejected_news:
            logger.info(f"Новость {getattr(rejected_news, 'id')} промодерирована: отклонена")
        
        # 9. Проверяем статистику
        logger.info("9. Проверка статистики...")
        all_news_after = await NewsCRUD.get_all_news(session)
        pending_news_after = await NewsCRUD.get_pending_news(session)
        approved_news = await NewsCRUD.get_approved_news(session)
        rejected_news_list = await NewsCRUD.get_rejected_news(session)
        
        logger.info(f"Всего новостей: {len(all_news_after)}")
        logger.info(f"Ожидают модерации: {len(pending_news_after)}")
        logger.info(f"Одобрено: {len(approved_news)}")
        logger.info(f"Отклонено: {len(rejected_news_list)}")
        
        # 10. Обновляем новость
        logger.info("10. Обновление новости...")
        updated_news = await NewsCRUD.update_news(
            session=session,
            news_id=getattr(news3, 'id'),
            title="Обновленный заголовок",
            content="Обновленное содержание"
        )
        if updated_news:
            logger.info(f"Новость {getattr(updated_news, 'id')} обновлена: '{getattr(updated_news, 'title')}'")

async def test_user_operations():
    """Тестирование операций с пользователями"""
    logger.info("\n=== Тестирование операций с пользователями ===")
    
    async with AsyncSessionLocal() as session:
        # 1. Создаем тестового пользователя
        logger.info("1. Создание тестового пользователя...")
        user = await UserCRUD.create_user(
            session=session,
            telegram_id=999999,
            username="test_user",
            first_name="Test",
            last_name="User",
            is_moderator=True
        )
        logger.info(f"Создан пользователь: ID={user.id}, Telegram ID={user.telegram_id}")
        
        # 2. Получаем пользователя по Telegram ID
        logger.info("2. Получение пользователя по Telegram ID...")
        retrieved_user = await UserCRUD.get_user_by_telegram_id(session, 999999)
        if retrieved_user:
            logger.info(f"Найден пользователь: {retrieved_user.username}")
        else:
            logger.error("Пользователь не найден!")
        
        # 3. Получаем всех модераторов
        logger.info("3. Получение всех модераторов...")
        moderators = await UserCRUD.get_moderators(session)
        logger.info(f"Найдено модераторов: {len(moderators)}")
        for moderator in moderators:
            logger.info(f"  - {moderator.username} (ID: {moderator.telegram_id})")
        
        # 4. Обновляем пользователя
        logger.info("4. Обновление пользователя...")
        updated_user = await UserCRUD.update_user(
            session=session,
            telegram_id=999999,
            first_name="Updated",
            last_name="Name"
        )
        if updated_user:
            logger.info(f"Пользователь обновлен: {updated_user.first_name} {updated_user.last_name}")

async def main():
    """Основная функция"""
    logger.info("Запуск тестирования...")
    
    try:
        # Тестируем операции с новостями
        await test_news_operations()
        
        # Тестируем операции с пользователями
        await test_user_operations()
        
        logger.info("\n=== Тестирование завершено успешно ===")
        
    except Exception as e:
        logger.error(f"Ошибка при тестировании: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 