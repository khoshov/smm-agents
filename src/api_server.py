#!/usr/bin/env python3
"""
Сервер для запуска FastAPI приложения SMM Agents
"""

import uvicorn
import sys
import os

# Добавляем корневую директорию в PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.api.app import app
from src.config.settings import settings

def main():
    """Запуск FastAPI сервера"""
    print("🚀 Запуск SMM Agents API сервера...")
    print(f"📊 Документация: http://localhost:8000/docs")
    print(f"🔍 ReDoc: http://localhost:8000/redoc")
    print(f"💚 Health check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Автоперезагрузка при изменениях
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main() 