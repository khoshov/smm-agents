from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from src.database.database import get_db
from src.database.crud import NewsCRUD, UserCRUD
from src.api.models import (
    NewsCreateRequest, NewsUpdateRequest, NewsModerateRequest,
    UserCreateRequest, NewsResponse, UserResponse, StatsResponse,
    PaginatedResponse, HealthResponse
)

router = APIRouter()

# Health check
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Проверка состояния API"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now()
    )

# News endpoints
@router.post("/news", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
    news_data: NewsCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание новой новости"""
    try:
        news = await NewsCRUD.create_news(
            session=db,
            title=news_data.title,
            content=news_data.content,
            url=str(news_data.url) if news_data.url else None
        )
        return NewsResponse.model_validate(news)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания новости: {str(e)}"
        )

@router.get("/news", response_model=PaginatedResponse)
async def get_news_list(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(20, ge=1, le=100, description="Размер страницы"),
    status_filter: Optional[str] = Query(None, description="Фильтр по статусу: pending, approved, rejected, published"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка новостей с пагинацией"""
    try:
        skip = (page - 1) * size
        
        # Получаем новости в зависимости от фильтра
        if status_filter == "pending":
            news_list = await NewsCRUD.get_pending_news(db)
            total = len(news_list)
        elif status_filter == "approved":
            news_list = await NewsCRUD.get_approved_news(db)
            total = len(news_list)
        elif status_filter == "rejected":
            news_list = await NewsCRUD.get_rejected_news(db)
            total = len(news_list)
        elif status_filter == "published":
            news_list = await NewsCRUD.get_published_news(db)
            total = len(news_list)
        else:
            # Получаем все новости с пагинацией
            all_news = await NewsCRUD.get_all_news(db)
            total = len(all_news)
            news_list = all_news[skip:skip + size]
        
        # Применяем пагинацию для отфильтрованных результатов
        if status_filter:
            news_list = news_list[skip:skip + size]
        
        pages = (total + size - 1) // size
        
        return PaginatedResponse(
            items=[NewsResponse.model_validate(news) for news in news_list],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения новостей: {str(e)}"
        )

@router.get("/news/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получение конкретной новости по ID"""
    try:
        news = await NewsCRUD.get_news(db, news_id)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Новость не найдена"
            )
        return NewsResponse.model_validate(news)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения новости: {str(e)}"
        )

@router.put("/news/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news_data: NewsUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Обновление новости"""
    try:
        update_data = {}
        if news_data.title is not None:
            update_data["title"] = news_data.title
        if news_data.content is not None:
            update_data["content"] = news_data.content
        if news_data.url is not None:
            update_data["url"] = str(news_data.url)
        
        news = await NewsCRUD.update_news(db, news_id, **update_data)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Новость не найдена"
            )
        return NewsResponse.model_validate(news)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка обновления новости: {str(e)}"
        )

@router.post("/news/{news_id}/moderate", response_model=NewsResponse)
async def moderate_news(
    news_id: int,
    moderation_data: NewsModerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Модерация новости"""
    try:
        news = await NewsCRUD.moderate_news(
            session=db,
            news_id=news_id,
            is_approved=moderation_data.is_approved,
            moderator_id=moderation_data.moderator_id,
            moderator_name=moderation_data.moderator_name
        )
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Новость не найдена"
            )
        return NewsResponse.model_validate(news)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка модерации новости: {str(e)}"
        )

@router.post("/news/{news_id}/publish", response_model=NewsResponse)
async def publish_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Публикация новости"""
    try:
        news = await NewsCRUD.publish_news(db, news_id)
        if not news:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Новость не найдена"
            )
        return NewsResponse.model_validate(news)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка публикации новости: {str(e)}"
        )

@router.delete("/news/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удаление новости"""
    try:
        deleted = await NewsCRUD.delete_news(db, news_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Новость не найдена"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка удаления новости: {str(e)}"
        )

# User endpoints
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового пользователя"""
    try:
        user = await UserCRUD.create_user(
            session=db,
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_moderator=user_data.is_moderator
        )
        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка создания пользователя: {str(e)}"
        )

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    """Получение списка пользователей"""
    try:
        users = await UserCRUD.get_all_users(db)
        return [UserResponse.model_validate(user) for user in users]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения пользователей: {str(e)}"
        )

@router.get("/users/moderators", response_model=List[UserResponse])
async def get_moderators(
    db: AsyncSession = Depends(get_db)
):
    """Получение списка модераторов"""
    try:
        moderators = await UserCRUD.get_moderators(db)
        return [UserResponse.model_validate(moderator) for moderator in moderators]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения модераторов: {str(e)}"
        )

# Statistics endpoints
@router.get("/stats", response_model=StatsResponse)
async def get_statistics(
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики системы"""
    try:
        # Получаем статистику новостей
        all_news = await NewsCRUD.get_all_news(db)
        pending_news = await NewsCRUD.get_pending_news(db)
        approved_news = await NewsCRUD.get_approved_news(db)
        rejected_news = await NewsCRUD.get_rejected_news(db)
        published_news = await NewsCRUD.get_published_news(db)
        
        # Получаем статистику пользователей
        all_users = await UserCRUD.get_all_users(db)
        moderators = await UserCRUD.get_moderators(db)
        
        return StatsResponse(
            total_news=len(all_news),
            pending_moderation=len(pending_news),
            approved_news=len(approved_news),
            rejected_news=len(rejected_news),
            published_news=len(published_news),
            total_users=len(all_users),
            active_moderators=len(moderators)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения статистики: {str(e)}"
        ) 