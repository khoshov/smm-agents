#!/bin/bash

# Скрипт для начальной настройки SMM Agents

set -e

echo "🚀 Настройка SMM Agents..."
echo "========================="

# Проверяем наличие UV
if ! command -v uv &> /dev/null; then
    echo "❌ UV не установлен. Устанавливаем..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
else
    echo "✅ UV уже установлен"
fi

# Проверяем наличие Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker не найден. Установите Docker для использования контейнеров"
fi

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
uv sync

# Создаем .env файл если не существует
if [ ! -f ".env" ]; then
    echo "📝 Создание .env файла..."
    cp .env.example .env
    echo "⚠️ Отредактируйте .env файл и добавьте ваши токены и настройки"
else
    echo "✅ .env файл уже существует"
fi

# Создаем директории для данных
echo "📁 Создание директорий..."
mkdir -p data logs

# Инициализируем базу данных
echo "🗄️ Инициализация базы данных..."
if [ -f "src/database/database.py" ]; then
    uv run python -c "
import asyncio
import sys
import os
sys.path.insert(0, '.')
from src.database.database import engine, Base
from src.database.models import User, News

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ База данных инициализирована')

asyncio.run(init_db())
"
else
    echo "⚠️ Файл database.py не найден, пропускаем инициализацию БД"
fi

# Применяем миграции если есть
if [ -d "migrations" ]; then
    echo "🔄 Применение миграций..."
    uv run alembic upgrade head
else
    echo "⚠️ Директория migrations не найдена"
fi

echo ""
echo "🎉 Настройка завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте .env файл с вашими токенами"
echo "2. Для запуска: uv run python src/main.py"
echo "3. Для Docker: cd docker && docker-compose up --build"
echo "4. Для тестов: uv run python -m pytest tests/" 