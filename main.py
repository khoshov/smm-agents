from agents.pipeline import run_news_pipeline
from config import settings
from loguru import logger

if __name__ == "__main__":
    # Настройки для сбора новостей
    KEYWORDS = ["искусственный интеллект", "машинное обучение", "нейросети", "AI", "ChatGPT", "OpenAI", "Google AI", "LLM"]
    RSS_FEEDS = [
        # Российские источники (проверенные)
        "https://habr.com/ru/rss/all/all/?fl=ru",
        "https://vc.ru/rss/all",
        "https://habr.com/ru/rss/hub/artificial_intelligence/",
        "https://habr.com/ru/rss/hub/machine_learning/",
        
        # Международные технологические источники (проверенные)
        "https://feeds.feedburner.com/venturebeat/SZYF",
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        
        # Технологические издания (рабочие ленты)
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        "https://www.wired.com/feed/rss",
        "https://feeds.arstechnica.com/arstechnica/index",
        
        # AI/Tech блоги (рабочие источники)
        "https://blog.google/technology/ai/rss/",
        "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "https://feeds.feedburner.com/TechCrunch",  # Дополнительный TechCrunch фид
    ]
    
    # Настройки для генерации изображений через OpenAI
    image_config = {
        "enabled": settings.generate_images and bool(settings.openai_api_key),
        "openai_api_key": settings.openai_api_key,
    }
    
    if image_config["enabled"]:
        logger.info("🎨 Генерация изображений включена (OpenAI DALL-E)")
    elif not settings.generate_images:
        logger.info("🎨 Генерация изображений отключена (GENERATE_IMAGES=False)")
    else:
        logger.info("🎨 Генерация изображений отключена (не указан OPENAI_API_KEY)")
    
    # Настраиваем источники новостей на основе флагов
    google_api = settings.google_api_key if settings.enable_google_news else None
    google_cse = settings.google_cse_id if settings.enable_google_news else None
    rss_feeds = RSS_FEEDS if settings.enable_rss_news else None
    
    # Логирование активных источников
    active_sources = []
    if settings.enable_google_news and google_api and google_cse:
        active_sources.append("Google Custom Search")
    if settings.enable_rss_news:
        active_sources.append(f"RSS ({len(RSS_FEEDS)} лент)")
    
    if not active_sources:
        logger.error("❌ Ни один источник новостей не активен!")
        exit(1)
    
    logger.info(f"📰 Активные источники: {', '.join(active_sources)}")
    logger.info(f"🕒 Период сбора RSS новостей: {settings.rss_hours_period} часов")
    
    # Запускаем полную цепочку: Scout → Filter → Copywriter → Image Generator
    final_posts = run_news_pipeline(
        keywords=KEYWORDS,
        flowise_host=settings.flowise_host,
        flowise_filter_id=settings.flowise_filter_id,
        flowise_copywriter_id=settings.flowise_copywriter_id,
        google_api=google_api,
        google_cse=google_cse,
        rss_feeds=rss_feeds,
        rss_hours=settings.rss_hours_period,
        max_per_source=5,
        image_config=image_config
    )
    
    # Выводим результаты
    if final_posts:
        logger.success(f"🎉 Получено {len(final_posts)} готовых постов!")
        
        for idx, post_data in enumerate(final_posts, 1):
            logger.info(f"\n📄 Пост #{idx}:")
            logger.info(f"Заголовок: {post_data['title']}")
            logger.info(f"URL: {post_data['url']}")
            logger.info(f"Контент поста:\n{post_data['post_content']}")
            logger.info(f"Идея изображения: {post_data['image_idea']}")
            
            if post_data.get('image_path'):
                logger.info(f"🖼️ Изображение: {post_data['image_path']}")
            else:
                logger.info("🖼️ Изображение: не создано")
                
            logger.info("-" * 80)
    else:
        logger.warning("😔 Не удалось создать ни одного поста")
