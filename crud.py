from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from models import User
from typing import Optional, List

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
        return result.scalars().all()
    
    @staticmethod
    async def get_moderators(session: AsyncSession) -> List[User]:
        """Получить всех модераторов"""
        result = await session.execute(
            select(User).where(User.is_moderator == True)
        )
        return result.scalars().all()
    
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