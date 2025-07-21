# API Документация SMM Agents

Подробная документация по программному интерфейсу системы модерации и публикации новостей.

## 📋 Обзор

SMM Agents предоставляет программный интерфейс для:
- Управления новостями (создание, модерация, публикация)
- Управления пользователями и модераторами
- Интеграции с Telegram ботами
- Статистики и отчетности

## 🗄️ База данных

### Модели данных

#### User (Пользователи)
```python
class User(Base):
    id: int                    # Первичный ключ
    telegram_id: int           # ID пользователя в Telegram (уникальный)
    username: str              # Имя пользователя
    first_name: str            # Имя
    last_name: str             # Фамилия
    is_active: bool            # Активен ли пользователь
    is_moderator: bool         # Является ли модератором
    created_at: datetime       # Дата создания
    updated_at: datetime       # Дата обновления
```

#### News (Новости)
```python
class News(Base):
    id: int                    # Первичный ключ
    url: str                   # URL источника новости (опционально)
    title: str                 # Заголовок новости
    content: str               # Текст новости
    is_moderated: bool         # Прошла ли модерацию
    is_approved: bool          # Одобрена ли новость (True/False/None)
    is_published: bool         # Опубликована ли в канале
    moderator_id: int          # ID модератора, который принял решение
    moderator_name: str        # Имя модератора
    published_at: datetime     # Время публикации
    created_at: datetime       # Дата создания
    updated_at: datetime       # Дата обновления
```

## 👥 API пользователей (UserCRUD)

### Создание пользователя
```python
from src.database.crud import UserCRUD
from src.database.database import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    user = await UserCRUD.create_user(
        session=session,
        telegram_id=12345678,
        username="user123",
        first_name="Иван",
        last_name="Петров",
        is_moderator=False
    )
```

### Получение пользователя
```python
# По Telegram ID
user = await UserCRUD.get_user_by_telegram_id(session, telegram_id=12345678)

# По ID в базе
user = await UserCRUD.get_user(session, user_id=1)

# Все пользователи
users = await UserCRUD.get_users(session, skip=0, limit=100)

# Только модераторы
moderators = await UserCRUD.get_moderators(session)
```

### Обновление пользователя
```python
# Назначение модератором
updated_user = await UserCRUD.update_user(
    session=session,
    user_id=1,
    is_moderator=True
)

# Обновление профиля
updated_user = await UserCRUD.update_user(
    session=session,
    user_id=1,
    first_name="Новое имя",
    username="new_username"
)
```

### Удаление пользователя
```python
deleted = await UserCRUD.delete_user(session, user_id=1)
```

## 📰 API новостей (NewsCRUD)

### Создание новости
```python
from src.database.crud import NewsCRUD

news = await NewsCRUD.create_news(
    session=session,
    title="Заголовок новости",
    content="Полный текст новости...",
    url="https://example.com/news/123"  # опционально
)
```

### Получение новостей
```python
# Все новости
all_news = await NewsCRUD.get_all_news(session, skip=0, limit=50)

# Ожидающие модерации
pending_news = await NewsCRUD.get_pending_news(session)

# Одобренные новости
approved_news = await NewsCRUD.get_approved_news(session)

# Отклоненные новости
rejected_news = await NewsCRUD.get_rejected_news(session)

# Опубликованные новости
published_news = await NewsCRUD.get_published_news(session)

# Одобренные, но не опубликованные
unpublished_approved = await NewsCRUD.get_unpublished_approved_news(session)

# Конкретная новость по ID
news = await NewsCRUD.get_news(session, news_id=1)
```

### Модерация новости
```python
# Одобрение новости
moderated_news = await NewsCRUD.moderate_news(
    session=session,
    news_id=1,
    is_approved=True,
    moderator_id=12345678,
    moderator_name="Модератор Иван"
)

# Отклонение новости
moderated_news = await NewsCRUD.moderate_news(
    session=session,
    news_id=1,
    is_approved=False,
    moderator_id=12345678,
    moderator_name="Модератор Иван"
)
```

### Публикация новости
```python
# Отметка новости как опубликованной
published_news = await NewsCRUD.publish_news(session, news_id=1)

# Публикация с указанием времени
from datetime import datetime
published_news = await NewsCRUD.publish_news(
    session, 
    news_id=1, 
    published_at=datetime.now()
)
```

### Обновление новости
```python
updated_news = await NewsCRUD.update_news(
    session=session,
    news_id=1,
    title="Обновленный заголовок",
    content="Обновленный текст"
)
```

### Удаление новости
```python
deleted = await NewsCRUD.delete_news(session, news_id=1)
```

## 🤖 API Telegram ботов

### Бот модератора (NewsModeratorBot)

#### Инициализация
```python
from src.bots.news_moderator_bot import NewsModeratorBot

bot = NewsModeratorBot(
    publisher_bot_token="токен_бота_издателя",
    channel_id="@канал_для_публикации"
)
```

#### Запуск бота
```python
# Запуск polling
await bot.start_polling()

# Остановка
await bot.stop_polling()
```

#### Отправка новости на модерацию
```python
# Отправка новости модераторам
await bot.send_news_for_moderation(news_id=1)

# Отправка новости конкретному модератору
await bot.send_news_to_moderator(news_id=1, moderator_telegram_id=12345678)
```

#### Статистика
```python
stats = await bot.get_moderation_stats()
# Возвращает:
# {
#     "total_news": 100,
#     "pending_moderation": 10,
#     "approved_news": 70,
#     "rejected_news": 20,
#     "published_news": 65
# }
```

### Бот издателя (PublisherBot)

#### Инициализация
```python
from src.bots.publisher_bot import PublisherBot

publisher = PublisherBot(
    bot_token="токен_бота_издателя",
    channel_id="@канал_для_публикации"
)
```

#### Публикация новостей
```python
# Публикация одной новости
success = await publisher.publish_single_news(news_id=1)

# Публикация всех одобренных новостей
results = await publisher.publish_pending_news()

# Публикация с форматированием
success = await publisher.publish_news_with_format(
    news_id=1,
    include_url=True,
    add_timestamp=True
)
```

#### Автоматическая публикация
```python
# Запуск цикла автоматической публикации
await publisher.start_publishing_loop(interval_seconds=300)  # каждые 5 минут

# Остановка цикла
await publisher.stop_publishing_loop()
```

#### Статистика издателя
```python
stats = await publisher.get_publishing_stats()
# Возвращает:
# {
#     "total_news": 100,
#     "approved_news": 70,
#     "published_news": 65,
#     "pending_publication": 5,
#     "failed_publications": 2
# }
```

## 🔍 API поиска и фильтрации

### Поиск новостей
```python
# Поиск по заголовку
news_by_title = await NewsCRUD.search_news_by_title(
    session, 
    search_term="искусственный интеллект"
)

# Поиск по содержимому
news_by_content = await NewsCRUD.search_news_by_content(
    session, 
    search_term="машинное обучение"
)

# Поиск по URL
news_by_url = await NewsCRUD.get_news_by_url(
    session, 
    url="https://example.com/news/123"
)
```

### Фильтрация по датам
```python
from datetime import datetime, timedelta

# Новости за последние 24 часа
recent_news = await NewsCRUD.get_news_by_date_range(
    session,
    start_date=datetime.now() - timedelta(days=1),
    end_date=datetime.now()
)

# Новости опубликованные сегодня
today_published = await NewsCRUD.get_published_news_by_date(
    session,
    date=datetime.now().date()
)
```

### Фильтрация по модератору
```python
# Новости, модерированные конкретным модератором
moderator_news = await NewsCRUD.get_news_by_moderator(
    session,
    moderator_id=12345678
)
```

## 📊 API статистики

### Общая статистика системы
```python
from src.database.crud import StatsCRUD

# Общая статистика
stats = await StatsCRUD.get_system_stats(session)
# Возвращает:
# {
#     "total_users": 50,
#     "active_moderators": 5,
#     "total_news": 1000,
#     "pending_moderation": 20,
#     "approved_news": 800,
#     "rejected_news": 180,
#     "published_news": 750,
#     "avg_moderation_time": "PT15M",  # 15 минут в ISO формате
#     "publication_rate": 0.9375  # 93.75%
# }
```

### Статистика по периодам
```python
# Статистика за период
period_stats = await StatsCRUD.get_stats_by_period(
    session,
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now()
)

# Ежедневная статистика
daily_stats = await StatsCRUD.get_daily_stats(session, days=30)
```

### Статистика модераторов
```python
# Производительность модераторов
moderator_stats = await StatsCRUD.get_moderator_performance(session)
# Возвращает список модераторов с их статистикой:
# [
#     {
#         "moderator_id": 12345678,
#         "moderator_name": "Иван",
#         "total_moderated": 100,
#         "approved": 85,
#         "rejected": 15,
#         "avg_time": "PT10M"
#     }
# ]
```

## 🔧 API утилит

### Сбор новостей (Scout)
```python
from src.utils.scout import collect_insights

insights = collect_insights(
    keywords=["искусственный интеллект", "AI"],
    google_api="your_google_api_key",
    google_cse="your_google_cse_id",
    rss_feeds=[
        "https://habr.com/ru/rss/all/all/?fl=ru",
        "https://vc.ru/rss/all/?fl=ru"
    ],
    max_per_source=5
)
```

### Копирайтинг (Copywriter)
```python
from src.utils.copywriter import call_flowise_copywriter

# Обработка статьи через Flowise
processed_article = call_flowise_copywriter(
    flow_id="your_flowise_flow_id",
    article={
        "title": "Заголовок",
        "content": "Содержимое статьи",
        "url": "https://example.com"
    },
    flowise_host="http://localhost:3000"
)
```

## 🔒 API безопасности

### Проверка прав доступа
```python
# Проверка, является ли пользователь модератором
is_moderator = await UserCRUD.is_moderator(session, telegram_id=12345678)

# Проверка активности пользователя
is_active = await UserCRUD.is_user_active(session, telegram_id=12345678)

# Получение прав пользователя
permissions = await UserCRUD.get_user_permissions(session, telegram_id=12345678)
```

### Аудит операций
```python
# Логирование действий модератора
await AuditCRUD.log_moderation_action(
    session=session,
    moderator_id=12345678,
    news_id=1,
    action="approved",
    timestamp=datetime.now()
)

# Получение истории действий
audit_log = await AuditCRUD.get_moderator_actions(
    session,
    moderator_id=12345678,
    limit=50
)
```

## 🚀 Примеры использования

### Полный цикл обработки новости
```python
async def process_news_article(article_data):
    """Полный цикл: создание → модерация → публикация"""
    
    async with AsyncSessionLocal() as session:
        # 1. Создание новости
        news = await NewsCRUD.create_news(
            session=session,
            title=article_data["title"],
            content=article_data["content"],
            url=article_data.get("url")
        )
        
        # 2. Отправка на модерацию
        bot = NewsModeratorBot()
        await bot.send_news_for_moderation(news.id)
        
        # 3. После модерации (в callback handler)
        # Этот код выполняется в обработчике callback'а
        if approved:
            await NewsCRUD.moderate_news(
                session=session,
                news_id=news.id,
                is_approved=True,
                moderator_id=moderator_telegram_id,
                moderator_name=moderator_name
            )
            
            # 4. Автоматическая публикация
            publisher = PublisherBot(bot_token, channel_id)
            success = await publisher.publish_single_news(news.id)
            
            if success:
                await NewsCRUD.publish_news(session, news.id)
```

### Массовая обработка новостей
```python
async def bulk_process_rss_feeds():
    """Массовая обработка RSS лент"""
    
    # Сбор новостей
    rss_feeds = [
        "https://habr.com/ru/rss/all/all/?fl=ru",
        "https://vc.ru/rss/all/?fl=ru"
    ]
    
    insights = collect_insights(
        keywords=["AI", "машинное обучение"],
        rss_feeds=rss_feeds,
        max_per_source=10
    )
    
    # Создание новостей в базе
    async with AsyncSessionLocal() as session:
        for article in insights:
            await NewsCRUD.create_news(
                session=session,
                title=article["title"],
                content=article["content"],
                url=article.get("url")
            )
    
    # Отправка на модерацию
    bot = NewsModeratorBot()
    pending_news = await NewsCRUD.get_pending_news(session)
    
    for news in pending_news:
        await bot.send_news_for_moderation(news.id)
```

## 🔧 Настройка и конфигурация

### Конфигурация через переменные окружения
```python
from src.config.settings import settings

# Доступ к настройкам
bot_token = settings.moderator_bot_token.get_secret_value()
channel_id = settings.channel_id
database_url = settings.database_url
```

### Настройка логирования
```python
import logging
from src.config.settings import settings

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format=settings.log_format
)
```

Эта документация покрывает основные возможности API системы SMM Agents. Для получения более подробной информации обращайтесь к исходному коду в соответствующих модулях. 