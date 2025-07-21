#!/usr/bin/env python3
"""
Главный модуль SMM Agents - система модерации и публикации новостей
"""

import sys
import os

# Добавляем корневую директорию в PATH для импортов
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.utils.copywriter import call_flowise_copywriter
from src.utils.scout import collect_insights
from src.config.settings import settings

def main():
    """Основная функция для запуска сбора и обработки новостей"""
    
    RSS_FEEDS = [
        "https://habr.com/ru/rss/all/all/?fl=ru",
        "https://vc.ru/rss/all/?fl=ru",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    ]

    try:
        insights = collect_insights(
            keywords=["искусственный интеллект", "AI", "машинное обучение"],
            google_api=settings.google_api_key,
            google_cse=settings.google_cse_id,
            rss_feeds=RSS_FEEDS,
            max_per_source=5,
        )

        print(f"Собрано {len(insights)} новостей")
        
        for idx, item in enumerate(insights, 1):
            print(f"\n[{idx}] Обрабатывается: {item.get('title', 'Без заголовка')[:50]}...")
            
            post = call_flowise_copywriter(
                flow_id=settings.flowise_id, 
                article=item, 
                flowise_host=settings.flowise_host
            )
            
            if post:
                print(f"✅ Статья обработана успешно")
            else:
                print(f"❌ Ошибка обработки статьи")
                
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 