from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime

# Модели для запросов
class NewsCreateRequest(BaseModel):
    title: str
    content: str
    url: Optional[HttpUrl] = None

class NewsUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[HttpUrl] = None

class NewsModerateRequest(BaseModel):
    is_approved: bool
    moderator_id: int
    moderator_name: str

class UserCreateRequest(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_moderator: bool = False

# Модели для ответов
class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    url: Optional[str] = None
    is_moderated: bool
    is_approved: Optional[bool] = None
    is_published: Optional[bool] = None
    moderator_id: Optional[int] = None
    moderator_name: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_moderator: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_news: int
    pending_moderation: int
    approved_news: int
    rejected_news: int
    published_news: int
    total_users: int
    active_moderators: int

class PaginatedResponse(BaseModel):
    items: List[NewsResponse]
    total: int
    page: int
    size: int
    pages: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str = "1.0.0" 