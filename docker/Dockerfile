FROM python:3.12-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем UV
RUN pip install uv

# Создаем пользователя для приложения
RUN useradd -m -s /bin/bash appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы управления зависимостями
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN uv sync --frozen

# Копируем исходный код
COPY src/ ./src/
COPY migrations/ ./migrations/
COPY scripts/ ./scripts/
COPY alembic.ini ./

# Создаем директории для данных
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Переключаемся на пользователя приложения
USER appuser

# Устанавливаем NLTK данные для пользователя appuser
RUN uv run python -c "import nltk; nltk.download('punkt_tab', quiet=True)"

# Открываем порт (если понадобится web интерфейс)
EXPOSE 8000

# Команда по умолчанию
CMD ["uv", "run", "python", "-m", "src.main"] 