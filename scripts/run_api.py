#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI сервера SMM Agents
"""

import sys
import os

# Добавляем корневую директорию в PATH
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.api_server import main

if __name__ == "__main__":
    main() 