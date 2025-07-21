"""
Агент Scout - модуль для сбора новостных статей из различных источников.

Основные функции:
- Поиск статей через Google Custom Search API
- Сбор статей из RSS-лент
- Извлечение и обработка содержимого статей
- Фильтрация нежелательных источников
"""

import requests
import feedparser
from newspaper import Article
from datetime import datetime, timedelta
from urllib.parse import urlparse
from typing import List, Dict, Optional
from loguru import logger
import ssl
import urllib3

# Отключаем предупреждения SSL для RSS лент
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Список доменов-агрегаторов, которые следует исключать из результатов
# Агрегаторы не предоставляют оригинальный контент, а лишь ссылаются на другие источники
BLOCKED_DOMAINS = {"news.google.com", "news.ycombinator.com"}


def is_valid_article(url: str) -> bool:
    """
    Проверяет, является ли URL допустимым источником статьи.
    
    Исключает агрегаторы и другие нежелательные домены.
    
    Args:
        url: URL для проверки
        
    Returns:
        bool: True, если URL допустим, False - если нет
    """
    domain = urlparse(url).netloc
    return domain not in BLOCKED_DOMAINS


def search_google_news(query: str, api_key: str, cse_id: str, num_results: int = 5) -> List[Dict[str, str]]:
    """
    Выполняет поиск новостей через Google Custom Search API.
    
    Использует специфические параметры для поиска актуальных новостей
    на русском языке, сортированных по дате публикации.
    
    Args:
        query: Поисковой запрос (ключевое слово)
        api_key: Ключ Google API
        cse_id: ID пользовательской поисковой системы Google
        num_results: Максимальное количество результатов (по умолчанию 5)
        
    Returns:
        List[Dict]: Список словарей с ключами 'title' и 'link'
    """
    url = "https://www.googleapis.com/customsearch/v1"
    
    # Список AI-focused сайтов для поиска
    ai_sites = [
        "habr.com", "vc.ru", "techcrunch.com", "venturebeat.com", 
        "artificialintelligence-news.com", "openai.com", "deepmind.com",
        "wired.com", "spectrum.ieee.org", "thenextweb.com"
    ]
    
    # Создаем поисковый запрос с множественными сайтами
    site_query = " OR ".join([f"site:{site}" for site in ai_sites])
    search_query = f"{query} ({site_query})"
    
    # Параметры поиска оптимизированы для получения свежих новостей
    params = {
        "q": search_query,              # Поиск по множественным AI сайтам
        "cx": cse_id,                   # ID пользовательской поисковой системы
        "key": api_key,                 # API ключ
        "num": num_results,             # Количество результатов
        "sort": "date",                 # Сортировка по дате
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        
        items = resp.json().get("items", [])
        
        # Фильтруем результаты, исключая заблокированные домены
        filtered_results = [
            {"title": item["title"], "link": item["link"]}
            for item in items
            if is_valid_article(item["link"])
        ]
        
        logger.debug(f"Google Search: найдено {len(filtered_results)} статей для запроса '{query}' по {len(ai_sites)} AI-сайтам")
        return filtered_results
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при поиске через Google API: {e}")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка при поиске: {e}")
        return []


def fetch_rss_headlines(feed_url: str, hours: int = 12) -> List[Dict[str, str]]:
    """
    Получает заголовки статей из RSS-ленты за указанный период.
    
    Фильтрует статьи по времени публикации, оставляя только свежие новости.
    
    Args:
        feed_url: URL RSS-ленты
        hours: Период в часах для фильтрации статей (по умолчанию 12)
        
    Returns:
        List[Dict]: Список словарей с ключами 'title' и 'link'
    """
    try:
        logger.debug(f"Начинаем парсинг RSS: {feed_url}")
        
        # Настраиваем SSL контекст для обхода проблем с сертификатами
        if hasattr(ssl, '_create_unverified_context'):
            ssl._create_default_https_context = ssl._create_unverified_context
        
        # Парсим RSS-ленту с дополнительными заголовками
        feed = feedparser.parse(feed_url, agent='Mozilla/5.0 (compatible; RSS Reader)')
        
        if feed.bozo:
            logger.warning(f"RSS лента может содержать ошибки: {feed_url}, ошибка: {feed.bozo_exception}")
            # Если есть записи, несмотря на ошибку, продолжаем
            if not feed.entries:
                logger.warning(f"RSS лента {feed_url} пуста, пропускаем")
                return []
        
        logger.debug(f"RSS {feed_url}: найдено {len(feed.entries)} записей всего")
        
        # Определяем временные рамки для фильтрации
        cutoff = datetime.now() - timedelta(hours=hours)
        news = []
        
        # Обрабатываем каждую запись в ленте
        for entry in feed.entries:
            try:
                # Получаем дату публикации (может отсутствовать)
                published = getattr(entry, "published_parsed", None)
                if not published:
                    # Если даты нет, берем текущую дату (для свежих лент)
                    logger.debug(f"Нет даты публикации для {entry.get('title', 'Unknown')}, используем как свежую")
                    published_dt = datetime.now()
                else:
                    # Конвертируем в объект datetime
                    published_dt = datetime(*published[:6])
                
                # Проверяем, что статья свежая и от допустимого источника
                if published_dt > cutoff and is_valid_article(entry.link):
                    news.append({
                        "title": entry.title,
                        "link": entry.link
                    })
                    logger.debug(f"Добавлена статья: {entry.title[:50]}...")
                elif published_dt <= cutoff:
                    logger.debug(f"Статья слишком старая: {entry.title[:50]}...")
                    
            except Exception as e:
                logger.debug(f"Ошибка обработки записи RSS: {e}")
                continue
        
        logger.debug(f"RSS {feed_url}: найдено {len(news)} свежих статей")
        return news
        
    except Exception as e:
        logger.error(f"Ошибка при обработке RSS {feed_url}: {e}")
        # Попытка с упрощенной обработкой
        try:
            logger.debug(f"Повторная попытка загрузки RSS с базовыми настройками: {feed_url}")
            
            # Простая загрузка без SSL проверок
            feed = feedparser.parse(feed_url)
            if feed.entries:
                logger.debug(f"Успешно загружено {len(feed.entries)} записей после повторной попытки")
                # Простая обработка без фильтрации по дате в случае проблем
                valid_entries = []
                for entry in feed.entries[:5]:  # Берем первые 5
                    if hasattr(entry, 'title') and hasattr(entry, 'link'):
                        valid_entries.append({
                            "title": entry.title,
                            "link": entry.link
                        })
                return valid_entries
        except Exception as e2:
            logger.error(f"Повторная попытка также неудачна для {feed_url}: {e2}")
        
        return []


def extract_summary(url: str) -> Optional[Dict[str, str]]:
    """
    Извлекает полный текст статьи и создает ее краткое содержание.
    
    Использует библиотеку newspaper3k для скачивания, парсинга
    и автоматического создания саммари статьи.
    
    Args:
        url: URL статьи для обработки
        
    Returns:
        Dict или None: Словарь с ключами 'title', 'summary', 'url' или None при ошибке
    """
    try:
        # Создаем объект статьи с указанием языка
        article = Article(url, language="ru")
        
        # Настраиваем заголовки для лучшей совместимости
        article.config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        article.config.request_timeout = 10
        
        # Скачиваем HTML-содержимое
        article.download()
        
        # Парсим статью (извлекаем заголовок, текст, метаданные)
        article.parse()
        
        # Проверяем базовые данные перед NLP
        if not article.title:
            logger.debug(f"Не удалось извлечь заголовок для {url}")
            return None
        
        # Выполняем NLP-обработку (создание саммари, извлечение ключевых слов)
        try:
            article.nlp()
        except Exception as nlp_error:
            logger.debug(f"NLP ошибка для {url}: {nlp_error}, используем текст статьи")
            # Если NLP не работает, создаем краткое саммари из текста
            if article.text:
                # Берем первые 2-3 предложения как саммари
                sentences = article.text.split('.')[:3]
                article.summary = '. '.join(sentences).strip() + '.'
        
        # Если саммари пустое, используем начало текста статьи
        if not article.summary and article.text:
            article.summary = article.text[:300] + "..."
        
        # Если все еще нет саммари, используем мета-описание
        if not article.summary:
            article.summary = f"Статья на тему: {article.title}"
        
        result = {
            "title": article.title.strip(),
            "summary": article.summary.strip(),
            "url": url
        }
        
        logger.debug(f"Успешно обработана статья: {article.title[:50]}...")
        return result
        
    except Exception as e:
        logger.debug(f"Ошибка при обработке {url}: {e}")
        return None


def collect_insights(keywords: List[str], 
                    google_api: Optional[str] = None, 
                    google_cse: Optional[str] = None, 
                    rss_feeds: Optional[List[str]] = None, 
                    rss_hours: int = 72,
                    max_per_source: int = 5) -> List[Dict[str, str]]:
    """
    Основная функция для сбора новостных инсайтов из различных источников.
    
    Комбинирует результаты поиска через Google Custom Search API и RSS-ленты,
    извлекает полное содержимое статей и возвращает структурированные данные.
    
    Args:
        keywords: Список ключевых слов для поиска
        google_api: Ключ Google API (опционально)
        google_cse: ID Google Custom Search Engine (опционально)
        rss_feeds: Список URL RSS-лент (опционально)
        rss_hours: Период в часах для фильтрации RSS (по умолчанию 72 часа)
        max_per_source: Максимальное количество статей с каждого источника
        
    Returns:
        List[Dict]: Список обработанных статей с заголовками, саммари и URL
    """
    results = []
    
    # Поиск через Google Custom Search API
    if google_api and google_cse:
        logger.info(f"🔍 Начинаем поиск через Google CSE для {len(keywords)} ключевых слов...")
        google_results_start = len(results)
        
        for kw in keywords:
            logger.debug(f"Поиск по ключевому слову: '{kw}'")
            
            # Получаем список статей по ключевому слову
            items = search_google_news(kw, google_api, google_cse, max_per_source)
            
            # Обрабатываем каждую найденную статью
            for item in items:
                summary = extract_summary(item["link"])
                if summary:
                    results.append(summary)
        
        google_results_count = len(results) - google_results_start            
        logger.info(f"✅ Google Search: обработано {google_results_count} статей")
    else:
        logger.info("⏭️  Google поиск отключен или не настроен")

    # Сбор из RSS-лент
    if rss_feeds:
        logger.info(f"📡 Начинаем обработку {len(rss_feeds)} RSS-лент...")
        rss_results_start = len(results)
        
        for feed_url in rss_feeds:
            logger.debug(f"Обрабатываем RSS: {feed_url}")
            
            # Получаем заголовки из RSS с указанным периодом
            items = fetch_rss_headlines(feed_url, rss_hours)
            
            # Обрабатываем ограниченное количество статей с каждой ленты
            processed_count = 0
            for item in items:
                if processed_count >= max_per_source:
                    break
                    
                summary = extract_summary(item["link"])
                if summary:
                    results.append(summary)
                    processed_count += 1
        
        rss_results_count = len(results) - rss_results_start            
        logger.info(f"✅ RSS: обработано {rss_results_count} статей из {len(rss_feeds)} лент")
    else:
        logger.info("⏭️  RSS ленты отключены")

    # Удаляем дубликаты по URL
    unique_results = []
    seen_urls = set()
    
    for result in results:
        if result["url"] not in seen_urls:
            unique_results.append(result)
            seen_urls.add(result["url"])
    
    logger.info(f"Собрано {len(unique_results)} уникальных статей (было {len(results)} до удаления дубликатов)")
    
    return unique_results
