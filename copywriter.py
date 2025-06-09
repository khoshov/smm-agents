import requests


def call_flowise_copywriter(flow_id, article, flowise_host):
    url = f"{flowise_host}/api/v1/prediction/{flow_id}"

    payload = {
        "question": f"Заголовок: {article['title']}, Краткое содержание: {article['summary']}, Ссылка: {article['url']}",
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    return response.json().get("text", "").strip()
