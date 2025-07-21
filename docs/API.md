# API Documentation

Подробная документация по API системы SMM Agents.

## 🌐 FastAPI Endpoints

### Базовый URL
```
http://localhost:8000/api/v1
```

### Документация
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Health Check

### Проверка состояния API
```http
GET /api/v1/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "version": "1.0.0"
}
```

## 📰 News API

### Создание новости
```http
POST /api/v1/news
```

**Тело запроса:**
```json
{
  "title": "Заголовок новости",
  "content": "Содержание новости",
  "url": "https://example.com/news"
}
```

**Ответ:**
```json
{
  "id": 1,
  "title": "Заголовок новости",
  "content": "Содержание новости",
  "url": "https://example.com/news",
  "is_moderated": false,
  "is_approved": null,
  "is_published": false,
  "moderator_id": null,
  "moderator_name": null,
  "published_at": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": null
}
```

### Получение списка новостей
```http
GET /api/v1/news?page=1&size=20&status_filter=pending
```

**Параметры:**
- `page` (int): Номер страницы (по умолчанию: 1)
- `size` (int): Размер страницы (по умолчанию: 20, максимум: 100)
- `status_filter` (string): Фильтр по статусу:
  - `pending` - ожидают модерации
  - `approved` - одобренные
  - `rejected` - отклоненные
  - `published` - опубликованные

**Ответ:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

### Получение конкретной новости
```http
GET /api/v1/news/{news_id}
```

### Обновление новости
```http
PUT /api/v1/news/{news_id}
```

**Тело запроса:**
```json
{
  "title": "Обновленный заголовок",
  "content": "Обновленное содержание"
}
```

### Модерация новости
```http
POST /api/v1/news/{news_id}/moderate
```

**Тело запроса:**
```json
{
  "is_approved": true,
  "moderator_id": 123456789,
  "moderator_name": "Иван Иванов"
}
```

### Публикация новости
```http
POST /api/v1/news/{news_id}/publish
```

### Удаление новости
```http
DELETE /api/v1/news/{news_id}
```

## 👥 Users API

### Создание пользователя
```http
POST /api/v1/users
```

**Тело запроса:**
```json
{
  "telegram_id": 123456789,
  "username": "user123",
  "first_name": "Иван",
  "last_name": "Иванов",
  "is_moderator": false
}
```

### Получение списка пользователей
```http
GET /api/v1/users
```

### Получение списка модераторов
```http
GET /api/v1/users/moderators
```

## 📈 Statistics API

### Получение статистики
```http
GET /api/v1/stats
```

**Ответ:**
```json
{
  "total_news": 150,
  "pending_moderation": 25,
  "approved_news": 100,
  "rejected_news": 15,
  "published_news": 80,
  "total_users": 50,
  "active_moderators": 5
}
```

## 🔧 Database CRUD API

### UserCRUD

#### Создание пользователя
```python
from src.database.crud import UserCRUD

user = await UserCRUD.create_user(
    session=db_session,
    telegram_id=123456789,
    username="user123",
    first_name="Иван",
    last_name="Иванов",
    is_moderator=False
)
```

#### Получение пользователя по Telegram ID
```python
user = await UserCRUD.get_user_by_telegram_id(db_session, 123456789)
```

#### Получение всех пользователей
```python
users = await UserCRUD.get_users(db_session)
```

#### Получение модераторов
```python
moderators = await UserCRUD.get_moderators(db_session)
```

#### Обновление пользователя
```python
updated_user = await UserCRUD.update_user(
    db_session, 
    user_id, 
    is_moderator=True
)
```

#### Удаление пользователя
```python
deleted = await UserCRUD.delete_user(db_session, user_id)
```

### NewsCRUD

#### Создание новости
```python
from src.database.crud import NewsCRUD

news = await NewsCRUD.create_news(
    session=db_session,
    title="Заголовок",
    content="Содержание",
    url="https://example.com"
)
```

#### Получение новости по ID
```python
news = await NewsCRUD.get_news(db_session, news_id)
```

#### Получение всех новостей
```python
all_news = await NewsCRUD.get_all_news(db_session)
```

#### Получение новостей по статусу
```python
pending_news = await NewsCRUD.get_pending_news(db_session)
approved_news = await NewsCRUD.get_approved_news(db_session)
rejected_news = await NewsCRUD.get_rejected_news(db_session)
published_news = await NewsCRUD.get_published_news(db_session)
```

#### Модерация новости
```python
moderated_news = await NewsCRUD.moderate_news(
    session=db_session,
    news_id=news_id,
    is_approved=True,
    moderator_id=123456789,
    moderator_name="Модератор"
)
```

#### Публикация новости
```python
published_news = await NewsCRUD.publish_news(db_session, news_id)
```

#### Обновление новости
```python
updated_news = await NewsCRUD.update_news(
    db_session, 
    news_id, 
    title="Новый заголовок"
)
```

#### Удаление новости
```python
deleted = await NewsCRUD.delete_news(db_session, news_id)
```

## 🤖 Bot API

### NewsModeratorBot

#### Инициализация
```python
from src.bots.news_moderator_bot import NewsModeratorBot

bot = NewsModeratorBot(
    publisher_bot_token="your_publisher_token",
    channel_id="@your_channel"
)
```

#### Запуск бота
```python
await bot.start_polling()
```

#### Остановка бота
```python
await bot.stop_polling()
```

#### Команды бота
- `/start` - Приветствие
- `/moderator` - Получение прав модератора
- `/stats` - Статистика
- `/publish` - Публикация новостей

### PublisherBot

#### Инициализация
```python
from src.bots.publisher_bot import PublisherBot

publisher = PublisherBot(
    bot_token="your_publisher_token",
    channel_id="@your_channel"
)
```

#### Запуск цикла публикации
```python
await publisher.start_publishing_loop(interval_seconds=300)
```

#### Остановка цикла публикации
```python
await publisher.stop_publishing_loop()
```

#### Публикация новости
```python
await publisher.publish_news(news_item)
```

## 🔍 Search & Filter API

### Поиск новостей
```python
from src.database.crud import NewsCRUD

# Поиск по заголовку
news = await NewsCRUD.search_news_by_title(db_session, "ключевое слово")

# Поиск по содержанию
news = await NewsCRUD.search_news_by_content(db_session, "ключевое слово")
```

### Фильтрация новостей
```python
# По дате создания
from datetime import datetime, timedelta

start_date = datetime.now() - timedelta(days=7)
recent_news = await NewsCRUD.get_news_by_date_range(
    db_session, 
    start_date, 
    datetime.now()
)

# По модератору
moderator_news = await NewsCRUD.get_news_by_moderator(
    db_session, 
    moderator_id
)
```

## 📊 Statistics API

### Получение статистики
```python
from src.database.crud import NewsCRUD, UserCRUD

# Статистика новостей
all_news = await NewsCRUD.get_all_news(db_session)
pending_news = await NewsCRUD.get_pending_news(db_session)
approved_news = await NewsCRUD.get_approved_news(db_session)
rejected_news = await NewsCRUD.get_rejected_news(db_session)
published_news = await NewsCRUD.get_published_news(db_session)

# Статистика пользователей
all_users = await UserCRUD.get_users(db_session)
moderators = await UserCRUD.get_moderators(db_session)
```

## 🛠 Utility API

### Scout (Сбор новостей)
```python
from src.utils.scout import collect_insights

insights = await collect_insights(
    keywords=["искусственный интеллект", "AI"],
    google_api="your_google_api_key",
    google_cse="your_google_cse_id",
    rss_feeds=["https://habr.com/ru/rss/all/all/?fl=ru"],
    max_per_source=5
)
```

### Copywriter (Обработка текста)
```python
from src.utils.copywriter import call_flowise_copywriter

post = await call_flowise_copywriter(
    flow_id="your_flow_id",
    article=news_item,
    flowise_host="http://localhost:3000"
)
```

## 🔐 Security API

### Проверка прав модератора
```python
from src.database.crud import UserCRUD

is_moderator = await UserCRUD.is_moderator(db_session, telegram_id)
```

### Активация/деактивация пользователя
```python
# Активация
await UserCRUD.activate_user(db_session, user_id)

# Деактивация
await UserCRUD.deactivate_user(db_session, user_id)
```

## 📝 Usage Examples

### Полный цикл работы с новостью

```python
import asyncio
from src.database.database import AsyncSessionLocal
from src.database.crud import NewsCRUD, UserCRUD
from src.utils.scout import collect_insights

async def full_news_cycle():
    async with AsyncSessionLocal() as session:
        # 1. Собираем новости
        insights = await collect_insights(
            keywords=["технологии"],
            google_api="your_key",
            google_cse="your_cse",
            rss_feeds=["https://habr.com/ru/rss/all/all/?fl=ru"]
        )
        
        # 2. Создаем новости в БД
        for insight in insights:
            news = await NewsCRUD.create_news(
                session=session,
                title=insight.get('title', ''),
                content=insight.get('summary', ''),
                url=insight.get('url')
            )
            print(f"Создана новость: {news.title}")
        
        # 3. Получаем статистику
        pending = await NewsCRUD.get_pending_news(session)
        print(f"Ожидают модерации: {len(pending)} новостей")

# Запуск
asyncio.run(full_news_cycle())
```

### Интеграция с внешними системами

```python
import httpx
import asyncio

async def external_integration():
    async with httpx.AsyncClient() as client:
        # Получаем список новостей через API
        response = await client.get("http://localhost:8000/api/v1/news")
        news_list = response.json()
        
        # Создаем новую новость
        new_news = {
            "title": "Новость из внешней системы",
            "content": "Содержание новости",
            "url": "https://example.com"
        }
        
        response = await client.post(
            "http://localhost:8000/api/v1/news",
            json=new_news
        )
        
        if response.status_code == 201:
            news_id = response.json()["id"]
            
            # Модерируем новость
            moderation_data = {
                "is_approved": True,
                "moderator_id": 123456789,
                "moderator_name": "Внешний модератор"
            }
            
            await client.post(
                f"http://localhost:8000/api/v1/news/{news_id}/moderate",
                json=moderation_data
            )

# Запуск
asyncio.run(external_integration())
```

## 🚀 Performance Tips

### Оптимизация запросов
```python
# Используйте пагинацию для больших списков
news = await NewsCRUD.get_all_news(session, skip=0, limit=20)

# Используйте фильтры для уменьшения объема данных
pending_news = await NewsCRUD.get_pending_news(session)
```

### Кэширование
```python
# Кэшируйте часто запрашиваемые данные
from functools import lru_cache

@lru_cache(maxsize=128)
def get_cached_stats():
    # Логика получения статистики
    pass
```

### Асинхронная обработка
```python
# Используйте asyncio.gather для параллельной обработки
tasks = [
    NewsCRUD.get_pending_news(session),
    NewsCRUD.get_approved_news(session),
    UserCRUD.get_moderators(session)
]

results = await asyncio.gather(*tasks)
```

## 🔧 Error Handling

### Обработка ошибок в API
```python
from fastapi import HTTPException

try:
    news = await NewsCRUD.get_news(session, news_id)
    if not news:
        raise HTTPException(status_code=404, detail="Новость не найдена")
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### Логирование ошибок
```python
import logging

logger = logging.getLogger(__name__)

try:
    # Операция с БД
    pass
except Exception as e:
    logger.error(f"Ошибка при работе с БД: {e}")
    raise
```

Эта документация покрывает все основные возможности API системы SMM Agents! 