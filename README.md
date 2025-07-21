# SMM Agents - Система модерации и публикации новостей

Современная автоматизированная система для сбора, модерации и публикации новостей через Telegram ботов с использованием асинхронной архитектуры Python.

## 🚀 Возможности

- ✅ **Автоматический сбор новостей** из RSS лент и Google поиска
- ✅ **Модерация через Telegram бота** с удобным интерфейсом
- ✅ **Автоматическая публикация** одобренных новостей в каналы
- ✅ **Асинхронная архитектура** для высокой производительности
- ✅ **Docker контейнеризация** для простого развертывания
- ✅ **База данных SQLite/PostgreSQL** с системой миграций
- ✅ **Comprehensive API** для интеграции с внешними системами
- ✅ **Graceful shutdown** и обработка сигналов
- ✅ **Логирование и мониторинг** всех операций
- ✅ **Система пользователей и модераторов**

## 🏗 Архитектура проекта

```
smm-agents/
├── src/                    # Основной код приложения
│   ├── bots/              # Telegram боты
│   ├── database/          # Модели и работа с БД
│   ├── config/           # Конфигурация
│   ├── utils/            # Утилиты
│   └── main.py           # Точка входа
├── tests/                # Тестовые файлы
├── docs/                 # Документация
├── docker/               # Docker файлы
├── scripts/              # Скрипты развертывания
├── migrations/           # Миграции базы данных
└── pyproject.toml        # Конфигурация проекта
```

## Структура базы данных

### Таблица `users`
- `id` - первичный ключ
- `telegram_id` - ID пользователя в Telegram (уникальный)
- `username` - имя пользователя
- `first_name` - имя
- `last_name` - фамилия
- `is_active` - активен ли пользователь
- `is_moderator` - является ли модератором
- `created_at` - дата создания
- `updated_at` - дата обновления

### Таблица `news`
- `id` - первичный ключ
- `url` - URL источника новости (опционально)
- `title` - заголовок новости
- `content` - текст новости
- `is_moderated` - прошла ли модерацию
- `is_approved` - одобрена ли новость (True/False/None)
- `is_published` - опубликована ли в канале
- `moderator_id` - ID модератора, который принял решение
- `moderator_name` - имя модератора
- `published_at` - время публикации
- `created_at` - дата создания
- `updated_at` - дата обновления

## 🚀 Быстрый старт

### Автоматическая установка
```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd smm-agents

# 2. Запустите скрипт установки
chmod +x scripts/setup.sh
./scripts/setup.sh

# 3. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env файл с вашими токенами
```

### Docker развертывание
```bash
# 1. Настройте .env файл
cp .env.example .env
# Отредактируйте .env с вашими настройками

# 2. Запустите с Docker Compose
cd docker
docker-compose up --build -d
```

### Конфигурация .env файла
```env
# Telegram Bot Tokens (обязательно)
MODERATOR_BOT_TOKEN=ваш_токен_модератора
PUBLISHER_BOT_TOKEN=ваш_токен_издателя
CHANNEL_ID=@ваш_канал

# Google API (опционально)
GOOGLE_API_KEY=ваш_google_api_ключ
GOOGLE_CSE_ID=ваш_google_cse_id

# Flowise (опционально)
FLOWISE_HOST=http://localhost:3000
FLOWISE_ID=ваш_flowise_id
```

## 🔧 Использование

### Запуск системы
```bash
# Локальный запуск
uv run python scripts/run_system.py

# Docker запуск
cd docker
docker-compose up --build

# Запуск только сбора новостей
uv run python src/main.py
```

### Команды бота модератора
- `/start` - регистрация в системе
- `/moderator` - получение прав модератора
- `/stats` - просмотр статистики новостей
- `/publish` - ручная публикация одобренных новостей

### Настройка публикации

1. **Создайте бота для публикации** через @BotFather
2. **Добавьте бота в канал** как администратора с правами на публикацию
3. **Получите ID канала** (например, "@your_channel" или "-1001234567890")
4. **Обновите токены** в коде или конфигурации

### Автоматическая публикация

При одобрении новости модератором она автоматически публикуется в канал (если настроен бот издателя).

## Тестирование

#### Простой тест
```bash
python simple_test.py
```

#### Тест с отладкой callback'ов
```bash
python debug_callback.py
```

#### Тест Ctrl+C
```bash
python test_ctrl_c.py
```

#### Тест работы с новостями
```bash
python test_news.py
```

#### Тест публикации
```bash
python test_publisher.py
```

#### Пример добавления новостей из внешнего источника
```bash
python add_news_example.py
```

## API для работы с новостями

### Создание новости
```python
from crud import NewsCRUD
from database import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    news = await NewsCRUD.create_news(
        session=session,
        title="Заголовок новости",
        content="Текст новости",
        url="https://example.com/news"
    )
```

### Получение новостей
```python
# Все новости
all_news = await NewsCRUD.get_all_news(session)

# Ожидающие модерации
pending_news = await NewsCRUD.get_pending_news(session)

# Одобренные
approved_news = await NewsCRUD.get_approved_news(session)

# Отклоненные
rejected_news = await NewsCRUD.get_rejected_news(session)

# Опубликованные
published_news = await NewsCRUD.get_published_news(session)

# Одобренные, но не опубликованные
unpublished_approved = await NewsCRUD.get_unpublished_approved_news(session)
```

### Модерация новости
```python
await NewsCRUD.moderate_news(
    session=session,
    news_id=1,
    is_approved=True,
    moderator_id=12345,
    moderator_name="Moderator Name"
)
```

### Публикация новости
```python
await NewsCRUD.publish_news(session, news_id=1)
```

## API для работы с публикацией

### Создание бота издателя
```python
from publisher_bot import PublisherBot

publisher = PublisherBot(
    bot_token="YOUR_PUBLISHER_BOT_TOKEN",
    channel_id="@your_channel"
)
```

### Публикация новостей
```python
# Публикация одной новости
success = await publisher.publish_single_news(news_id=1)

# Публикация всех одобренных новостей
results = await publisher.publish_pending_news()

# Запуск цикла автоматической публикации
await publisher.start_publishing_loop(interval_seconds=300)  # каждые 5 минут
```

### Получение статистики
```python
stats = await publisher.get_publishing_stats()
print(f"Всего новостей: {stats['total_news']}")
print(f"Одобрено: {stats['approved_news']}")
print(f"Опубликовано: {stats['published_news']}")
print(f"Ожидают публикации: {stats['pending_publication']}")
```

## Архитектура

### Основные компоненты

1. **NewsModeratorBot** - основной класс бота модератора
   - Обработка команд и callback'ов
   - Отправка новостей на модерацию
   - Интеграция с ботом издателя
   - Управление жизненным циклом бота

2. **PublisherBot** - класс бота издателя
   - Публикация новостей в канал
   - Форматирование сообщений
   - Автоматический цикл публикации
   - Статистика публикаций

3. **UserCRUD** - операции с пользователями
   - Создание, чтение, обновление пользователей
   - Управление правами модераторов

4. **NewsCRUD** - операции с новостями
   - CRUD операции для новостей
   - Модерация и публикация
   - Статистика

5. **Database** - настройка базы данных
   - Async SQLAlchemy
   - Миграции через Alembic

### Поток данных

1. **Добавление новости**: Внешний источник → База данных → Отправка модераторам
2. **Модерация**: Модератор → Кнопка одобрения/отклонения → Обновление в БД
3. **Публикация**: Одобренная новость → Автоматическая публикация в канал → Отметка как опубликованной
4. **Результат**: Полный цикл от добавления до публикации

### Статусы новостей

- **Ожидает модерации**: `is_moderated=False`, `is_approved=None`
- **Одобрена**: `is_moderated=True`, `is_approved=True`, `is_published=False`
- **Отклонена**: `is_moderated=True`, `is_approved=False`
- **Опубликована**: `is_moderated=True`, `is_approved=True`, `is_published=True`

## Разработка

### Добавление новых функций

1. Создайте миграцию для изменений в БД:
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

2. Обновите модели в `models.py`

3. Добавьте CRUD операции в `crud.py`

4. Обновите бота в `news_moderator_bot.py` или `publisher_bot.py`

### Логирование

Все операции логируются с использованием стандартного модуля `logging`. Уровень логирования можно настроить в начале каждого файла.

## Лицензия

MIT License