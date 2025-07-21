from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from src.database.models import User, News
from typing import Optional, List
from datetime import datetime

class UserCRUD:
    @staticmethod
    async def create_user(
        session: AsyncSession,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_moderator: bool = False
    ) -> User:
        """Создать нового пользователя"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_moderator=is_moderator
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
    
    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_users(session: AsyncSession) -> List[User]:
        """Получить всех пользователей"""
        result = await session.execute(select(User))
        return list(result.scalars().all())
    
    @staticmethod
    async def get_moderators(session: AsyncSession) -> List[User]:
        """Получить всех модераторов"""
        result = await session.execute(
            select(User).where(User.is_moderator == True)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update_user(
        session: AsyncSession,
        telegram_id: int,
        **kwargs
    ) -> Optional[User]:
        """Обновить пользователя"""
        user = await UserCRUD.get_user_by_telegram_id(session, telegram_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            await session.commit()
            await session.refresh(user)
        return user
    
    @staticmethod
    async def delete_user(session: AsyncSession, telegram_id: int) -> bool:
        """Удалить пользователя"""
        user = await UserCRUD.get_user_by_telegram_id(session, telegram_id)
        if user:
            await session.delete(user)
            await session.commit()
            return True
        return False
    
    @staticmethod
    async def set_moderator_status(
        session: AsyncSession,
        telegram_id: int,
        is_moderator: bool
    ) -> Optional[User]:
        """Установить статус модератора"""
        return await UserCRUD.update_user(
            session, telegram_id, is_moderator=is_moderator
        )

class NewsCRUD:
    @staticmethod
    async def create_news(
        session: AsyncSession,
        title: str,
        content: str,
        url: Optional[str] = None
    ) -> News:
        """Создать новую новость"""
        news = News(
            title=title,
            content=content,
            url=url,
            is_moderated=False,
            is_approved=None,
            is_published=False
        )
        session.add(news)
        await session.commit()
        await session.refresh(news)
        return news
    
    @staticmethod
    async def get_news_by_id(session: AsyncSession, news_id: int) -> Optional[News]:
        """Получить новость по ID"""
        result = await session.execute(
            select(News).where(News.id == news_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_news(session: AsyncSession) -> List[News]:
        """Получить все новости"""
        result = await session.execute(select(News).order_by(News.created_at.desc()))
        return list(result.scalars().all())
    
    @staticmethod
    async def get_pending_news(session: AsyncSession) -> List[News]:
        """Получить новости, ожидающие модерации"""
        result = await session.execute(
            select(News).where(News.is_moderated == False).order_by(News.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_approved_news(session: AsyncSession) -> List[News]:
        """Получить одобренные новости"""
        result = await session.execute(
            select(News).where(News.is_moderated == True, News.is_approved == True).order_by(News.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_rejected_news(session: AsyncSession) -> List[News]:
        """Получить отклоненные новости"""
        result = await session.execute(
            select(News).where(News.is_moderated == True, News.is_approved == False).order_by(News.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_unpublished_approved_news(session: AsyncSession) -> List[News]:
        """Получить одобренные, но не опубликованные новости"""
        result = await session.execute(
            select(News).where(
                News.is_moderated == True, 
                News.is_approved == True,
                News.is_published == False
            ).order_by(News.created_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def get_published_news(session: AsyncSession) -> List[News]:
        """Получить опубликованные новости"""
        result = await session.execute(
            select(News).where(News.is_published == True).order_by(News.published_at.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update_news(
        session: AsyncSession,
        news_id: int,
        **kwargs
    ) -> Optional[News]:
        """Обновить новость"""
        news = await NewsCRUD.get_news_by_id(session, news_id)
        if news:
            for key, value in kwargs.items():
                if hasattr(news, key):
                    setattr(news, key, value)
            await session.commit()
            await session.refresh(news)
        return news
    
    @staticmethod
    async def delete_news(session: AsyncSession, news_id: int) -> bool:
        """Удалить новость"""
        news = await NewsCRUD.get_news_by_id(session, news_id)
        if news:
            await session.delete(news)
            await session.commit()
            return True
        return False
    
    @staticmethod
    async def moderate_news(
        session: AsyncSession,
        news_id: int,
        is_approved: bool,
        moderator_id: Optional[int] = None,
        moderator_name: Optional[str] = None
    ) -> Optional[News]:
        """Модерировать новость"""
        return await NewsCRUD.update_news(
            session,
            news_id,
            is_moderated=True,
            is_approved=is_approved,
            moderator_id=moderator_id,
            moderator_name=moderator_name
        )
    
    @staticmethod
    async def publish_news(
        session: AsyncSession,
        news_id: int
    ) -> Optional[News]:
        """Отметить новость как опубликованную"""
        return await NewsCRUD.update_news(
            session,
            news_id,
            is_published=True,
            published_at=datetime.utcnow()
        )
    
    @staticmethod
    async def get_news_by_url(session: AsyncSession, url: str) -> Optional[News]:
        """Получить новость по URL"""
        result = await session.execute(
            select(News).where(News.url == url)
        )
        return result.scalar_one_or_none() 