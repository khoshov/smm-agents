import requests
import feedparser
from newspaper import Article
from datetime import datetime, timedelta
from urllib.parse import urlparse
from loguru import logger

# --- ИСКЛЮЧАЕМ АГРЕГАТОРЫ ---
BLOCKED_DOMAINS = {"news.google.com", "news.ycombinator.com"}


def is_valid_article(url):
    domain = urlparse(url).netloc
    return domain not in BLOCKED_DOMAINS


# --- GOOGLE NEWS ПОИСК ---
def search_google_news(query, api_key, cse_id, num_results=5):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query + " site:habr.com",
        "cx": cse_id,
        "key": api_key,
        "num": num_results,
        "sort": "date",
        "lr": "lang_ru",
    }
    resp = requests.get(url, params=params)
    items = resp.json().get("items", [])
    return [
        {"title": item["title"], "link": item["link"]}
        for item in items
        if is_valid_article(item["link"])
    ]


# --- RSS ОБРАБОТКА ---
def fetch_rss_headlines(feed_url, hours=12):
    feed = feedparser.parse(feed_url)
    cutoff = datetime.now() - timedelta(hours=hours)
    news = []
    for entry in feed.entries:
        published = getattr(entry, "published_parsed", None)
        if not published:
            continue
        published_dt = datetime(*published[:6])
        if published_dt > cutoff and is_valid_article(entry.link):
            news.append({"title": entry.title, "link": entry.link})
    return news


# --- СТАТЬИ ---
def extract_summary(url):
    try:
        article = Article(url, language="ru")
        article.download()
        article.parse()
        article.nlp()
        return {
            "title": article.title,
            "summary": article.summary,
            "url": url
        }
    except Exception as e:
        logger.debug(f"[!] Ошибка при обработке {url}: {e}")
        return None


# --- ОСНОВНАЯ ЛОГИКА ---
def collect_insights(keywords, google_api=None, google_cse=None, rss_feeds=None, max_per_source=5):
    results = []

    if google_api and google_cse:
        logger.debug("[*] Поиск по Google CSE...")
        for kw in keywords:
            items = search_google_news(kw, google_api, google_cse, max_per_source)
            for item in items:
                summary = extract_summary(item["link"])
                if summary:
                    results.append(summary)

    if rss_feeds:
        logger.debug("[*] Поиск в RSS...")
        for feed_url in rss_feeds:
            items = fetch_rss_headlines(feed_url)
            for item in items[:max_per_source]:
                summary = extract_summary(item["link"])
                if summary:
                    results.append(summary)

    return results
