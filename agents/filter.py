import requests
from typing import List, Dict
from loguru import logger


def check_relevance_with_flowise(article: Dict[str, str], flow_id: str, flowise_host: str) -> Dict[str, any]:
    url = f"{flowise_host}/api/v1/prediction/{flow_id}"
    
    filter_prompt = f"Заголовок: {article.get('title', '')} Краткое содержание: {article.get('summary', '')}"

    payload = {"question": filter_prompt}
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result_text = response.json().get("text", "").strip()
        
        import json
        import re
        
        # Очищаем ответ от markdown блоков
        clean_text = result_text
        if "```json" in result_text:
            # Извлекаем JSON из markdown блока
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', result_text, re.DOTALL)
            if json_match:
                clean_text = json_match.group(1)
        
        try:
            result = json.loads(clean_text)
            is_news = result.get('is_news', False)
            is_ai_related = result.get('is_ai_related', False)
            
            return {
                'is_relevant': is_news and is_ai_related,
                'is_news': is_news,
                'is_ai_related': is_ai_related,
                'reasoning': result.get('reasoning', 'Нет объяснения')
            }
        except json.JSONDecodeError:
            logger.warning(f"Не удалось парсить JSON ответ: {result_text}")
            return {'is_relevant': False, 'is_news': False, 'is_ai_related': False, 'reasoning': 'Ошибка парсинга ответа'}
                
    except Exception as e:
        logger.error(f"Ошибка при проверке релевантности через Flowise: {e}")
        return {'is_relevant': False, 'is_news': False, 'is_ai_related': False, 'reasoning': 'Ошибка API'}


def filter_news_with_flowise(articles: List[Dict[str, str]], 
                            flow_id: str, 
                            flowise_host: str) -> List[Dict[str, str]]:
    
    filtered_articles = []
    
    for article in articles:
        relevance_check = check_relevance_with_flowise(article, flow_id, flowise_host)
        
        if relevance_check['is_relevant']:
            article_with_meta = article.copy()
            article_with_meta['is_news'] = relevance_check['is_news']
            article_with_meta['is_ai_related'] = relevance_check['is_ai_related']
            article_with_meta['filter_reasoning'] = relevance_check['reasoning']
            filtered_articles.append(article_with_meta)
            logger.debug(f"✓ Статья прошла фильтр: {article['title'][:50]}... (Новость: {relevance_check['is_news']}, ИИ: {relevance_check['is_ai_related']})")
        else:
            logger.debug(f"✗ Статья отклонена: {article['title'][:50]}... Причина: {relevance_check['reasoning']}")
    
    return filtered_articles