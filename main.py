from copywriter import call_flowise_copywriter
from scout import collect_insights
from config import settings

if __name__ == "__main__":

    RSS_FEEDS = [
        "https://habr.com/ru/rss/all/all/?fl=ru",
        "https://vc.ru/rss/all",
        "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"
    ]

    insights = collect_insights(
        keywords=["искусственный интеллект"],
        google_api=settings.google_api_key,
        google_cse=settings.google_cse_id,
        rss_feeds=RSS_FEEDS,
        max_per_source=5,
    )

    for idx, item in enumerate(insights, 1):
        post = call_flowise_copywriter(flow_id=settings.flowise_id, article=item, flowise_host=settings.flowise_host)
