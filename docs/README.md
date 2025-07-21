# SMM Agents - Система модерации и публикации новостей

Автоматизированная система для сбора, модерации и публикации новостей через Telegram ботов с использованием современных технологий Python.

## 🚀 Возможности

- ✅ **Автоматический сбор новостей** из RSS лент и Google поиска
- ✅ **Модерация через Telegram бота** с удобным интерфейсом
- ✅ **Автоматическая публикация** одобренных новостей в каналы
- ✅ **Асинхронная архитектура** для высокой производительности
- ✅ **База данных SQLite/PostgreSQL** для хранения новостей и пользователей
- ✅ **Docker контейнеризация** для простого развертывания
- ✅ **Система миграций** для управления схемой БД
- ✅ **Comprehensive API** для интеграции с внешними системами
- ✅ **Graceful shutdown** и обработка сигналов
- ✅ **Логирование и мониторинг** всех операций

## 📁 Структура проекта

```
smm-agents/
├── src/                    # Основной код приложения
│   ├── bots/              # Telegram боты
│   │   ├── news_moderator_bot.py
│   │   ├── publisher_bot.py
│   │   └── __init__.py
│   ├── database/          # Модели и работа с БД
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── crud.py
│   │   └── __init__.py
│   ├── config/           # Конфигурация
│   │   ├── settings.py
│   │   └── __init__.py
│   ├── utils/            # Утилиты
│   │   ├── copywriter.py
│   │   ├── scout.py
│   │   └── __init__.py
│   ├── main.py           # Точка входа
│   └── __init__.py
├── tests/                # Тестовые файлы
├── docs/                 # Документация
├── docker/               # Docker файлы
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/              # Скрипты развертывания
│   ├── setup.sh
│   └── run_system.py
├── migrations/           # Миграции базы данных
├── data/                 # Данные приложения
├── logs/                 # Логи
├── pyproject.toml        # Конфигурация проекта
├── .env.example          # Пример переменных окружения
└── README.md
```

## 🛠 Установка и настройка

### Быстрый старт

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

### Ручная установка

1. **Установите UV (если не установлен):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Установите зависимости:**
```bash
uv sync
```

3. **Настройте переменные окружения:**
```bash
cp .env.example .env
```

Отредактируйте `.env` файл:
```env
# Telegram Bot Tokens
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

4. **Инициализируйте базу данных:**
```bash
uv run python -c "
import asyncio
from src.database.database import engine, Base
from src.database.models import User, News

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('База данных инициализирована')

asyncio.run(init_db())
"
```

## 🐳 Docker развертывание

### Быстрый запуск с Docker

```bash
# 1. Настройте .env файл
cp .env.example .env
# Отредактируйте .env с вашими настройками

# 2. Запустите с Docker Compose
cd docker
docker-compose up --build -d

# 3. Проверьте логи
docker-compose logs -f app
```

### Развертывание только приложения

```bash
# Сборка образа
docker build -f docker/Dockerfile -t smm-agents .

# Запуск контейнера
docker run -d \
  --name smm-agents \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  smm-agents
```

## 🚀 Использование

### Запуск системы

#### Локальный запуск
```bash
# Запуск сбора новостей
uv run python src/main.py

# Запуск системы ботов
uv run python scripts/run_system.py
```

#### Docker запуск
```bash
cd docker
docker-compose up --build
```

### Команды Telegram ботов

#### Бот модератора
- `/start` - регистрация в системе
- `/moderator` - получение прав модератора
- `/stats` - просмотр статистики новостей
- `/publish` - ручная публикация одобренных новостей

#### Процесс модерации
1. Новости автоматически отправляются модераторам
2. Модератор нажимает "✅ Одобрить" или "❌ Отклонить"
3. Одобренные новости автоматически публикуются в канал

### API для работы с новостями

```python
from src.database.crud import NewsCRUD
from src.database.database import AsyncSessionLocal

# Создание новости
async with AsyncSessionLocal() as session:
    news = await NewsCRUD.create_news(
        session=session,
        title="Заголовок новости",
        content="Текст новости",
        url="https://example.com/news"
    )

# Получение новостей
pending_news = await NewsCRUD.get_pending_news(session)
approved_news = await NewsCRUD.get_approved_news(session)

# Модерация
await NewsCRUD.moderate_news(
    session=session,
    news_id=1,
    is_approved=True,
    moderator_id=12345,
    moderator_name="Moderator Name"
)
```

## 🧪 Тестирование

```bash
# Запуск всех тестов
uv run python -m pytest tests/

# Запуск конкретного теста
uv run python tests/simple_test.py

# Тест с отладкой
uv run python tests/debug_callback.py
```

## 📊 Мониторинг и логирование

### Логи
- Логи сохраняются в директории `logs/`
- Уровень логирования настраивается в `.env`: `LOG_LEVEL=INFO`

### База данных
- SQLite (по умолчанию): `telegram_bot.db`
- PostgreSQL (для Docker): настраивается в docker-compose.yml
- Adminer доступен на `http://localhost:8081` (в Docker)

### Статистика
```bash
# Через бота модератора
/stats

# Через API
from src.bots.publisher_bot import PublisherBot
stats = await publisher_bot.get_publishing_stats()
```

## 🔧 Разработка

### Добавление новых функций

1. **Изменения в базе данных:**
```bash
# Создание миграции
uv run alembic revision --autogenerate -m "Описание изменений"

# Применение миграции
uv run alembic upgrade head
```

2. **Обновление зависимостей:**
```bash
# Добавление новой зависимости
uv add package_name

# Обновление зависимостей
uv sync
```

3. **Тестирование:**
```bash
# Запуск тестов
uv run python -m pytest tests/ -v

# Линтинг
uv run ruff check src/
uv run black src/
```

### Структура модулей

- `src/bots/` - Telegram боты и их логика
- `src/database/` - Модели, CRUD операции, подключение к БД
- `src/config/` - Конфигурация и настройки
- `src/utils/` - Вспомогательные функции (копирайтинг, сбор данных)
- `tests/` - Все тестовые файлы
- `scripts/` - Скрипты для развертывания и администрирования

## 🔒 Безопасность

- Все токены и пароли хранятся в переменных окружения
- База данных изолирована в Docker сети
- Graceful shutdown предотвращает потерю данных
- Валидация входных данных через Pydantic

## 📈 Производительность

- Асинхронная архитектура для высокой пропускной способности
- Пулы соединений к базе данных
- Оптимизированные SQL запросы
- Кэширование часто используемых данных

## 🐛 Устранение неполадок

### Частые проблемы

1. **Ошибка токена бота:**
```bash
# Проверьте .env файл
cat .env | grep BOT_TOKEN
```

2. **Проблемы с базой данных:**
```bash
# Пересоздание БД
rm telegram_bot.db
uv run python scripts/setup.sh
```

3. **Docker проблемы:**
```bash
# Пересборка контейнеров
docker-compose down -v
docker-compose up --build
```

### Логи и отладка

```bash
# Проверка логов Docker
docker-compose logs -f app

# Проверка состояния контейнеров
docker-compose ps

# Подключение к контейнеру
docker-compose exec app bash
```

## 📝 Лицензия

MIT License - см. файл LICENSE

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для функции (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Запушьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request 