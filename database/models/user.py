from sqlalchemy import Column, BigInteger, String, Integer, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True)
    steam_id = Column(BigInteger, unique=True, nullable=True)
    
    username = Column(String, nullable=True)
    
    # ВОТ ЭТА КОЛОНКА ОТВЕЧАЕТ ЗА ЯЗЫК
    language = Column(String, default="ru") 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связь с библиотекой
    library = relationship("UserLibrary", back_populates="user", cascade="all, delete-orphan")

class UserLibrary(Base):
    __tablename__ = "user_library"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.telegram_id"), index=True)
    game_id = Column(BigInteger, ForeignKey("games.id"), index=True)
    
    playtime_forever = Column(Integer, default=0) # Минуты
    playtime_2weeks = Column(Integer, default=0)
    
    user = relationship("User", back_populates="library")