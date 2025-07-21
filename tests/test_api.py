#!/usr/bin/env python3
"""
Тесты для FastAPI endpoints
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.api.app import app

# Синхронный клиент для тестов
client = TestClient(app)

def test_root_endpoint():
    """Тест корневого endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "SMM Agents API"
    assert data["version"] == "1.0.0"

def test_health_endpoint():
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_api_health_endpoint():
    """Тест API health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_news_list_endpoint():
    """Тест получения списка новостей"""
    response = client.get("/api/v1/news")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "size" in data
    assert "pages" in data

def test_news_list_with_pagination():
    """Тест пагинации списка новостей"""
    response = client.get("/api/v1/news?page=1&size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["size"] == 10

def test_news_list_with_filter():
    """Тест фильтрации списка новостей"""
    response = client.get("/api/v1/news?status_filter=pending")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

def test_stats_endpoint():
    """Тест получения статистики"""
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_news" in data
    assert "pending_moderation" in data
    assert "approved_news" in data
    assert "rejected_news" in data
    assert "published_news" in data
    assert "total_users" in data
    assert "active_moderators" in data

def test_users_endpoint():
    """Тест получения списка пользователей"""
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_moderators_endpoint():
    """Тест получения списка модераторов"""
    response = client.get("/api/v1/users/moderators")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_create_news_endpoint():
    """Тест создания новости"""
    news_data = {
        "title": "Тестовая новость",
        "content": "Содержание тестовой новости",
        "url": "https://example.com/test"
    }
    response = client.post("/api/v1/news", json=news_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == news_data["title"]
    assert data["content"] == news_data["content"]
    assert data["url"] == news_data["url"]

def test_create_news_invalid_data():
    """Тест создания новости с неверными данными"""
    news_data = {
        "title": "",  # Пустой заголовок
        "content": "Содержание"
    }
    response = client.post("/api/v1/news", json=news_data)
    assert response.status_code == 400

def test_create_user_endpoint():
    """Тест создания пользователя"""
    user_data = {
        "telegram_id": 123456789,
        "username": "test_user",
        "first_name": "Test",
        "last_name": "User",
        "is_moderator": False
    }
    response = client.post("/api/v1/users", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["telegram_id"] == user_data["telegram_id"]
    assert data["username"] == user_data["username"]

# Асинхронные тесты (если нужны)
@pytest.mark.asyncio
async def test_async_health_check():
    """Асинхронный тест health check"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"]) 