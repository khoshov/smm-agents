from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, Text
from sqlalchemy.sql import func
from src.database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_moderator = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username='{self.username}')>"

class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=True, index=True)  # URL источника новости
    title = Column(String, nullable=False)  # Заголовок новости
    content = Column(Text, nullable=False)  # Текст новости
    is_moderated = Column(Boolean, default=False)  # Статус модерации (True - прошла модерацию)
    is_approved = Column(Boolean, nullable=True)  # Результат одобрения (True - одобрено, False - отклонено, None - не рассмотрено)
    is_published = Column(Boolean, default=False)  # Статус публикации (True - опубликовано в канале)
    moderator_id = Column(BigInteger, nullable=True)  # ID модератора, который принял решение
    moderator_name = Column(String, nullable=True)  # Имя модератора
    published_at = Column(DateTime(timezone=True), nullable=True)  # Время публикации
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<News(id={self.id}, title='{self.title[:50]}...', is_moderated={self.is_moderated}, is_approved={self.is_approved}, is_published={self.is_published})>" 