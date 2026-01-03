from sqlalchemy import Column, BigInteger, String, Integer, Float, Boolean, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(BigInteger, primary_key=True)  # Steam AppID
    name = Column(String, index=True)
    
    # Экономика (Базовая в USD)
    price_current = Column(Float, default=0.0)
    is_free = Column(Boolean, default=False)
    currency = Column(String, default="USD")

    # Статистика
    reviews_total = Column(Integer, default=0)
    achievements_count = Column(Integer, default=0)
    release_date = Column(String, nullable=True)
    metacritic_score = Column(Integer, default=0)

    # HowLongToBeat
    time_main = Column(Float, default=0)
    time_plus = Column(Float, default=0)
    time_100 = Column(Float, default=0)
    hltb_id = Column(String, nullable=True)

    # JSON данные
    locales = Column(JSON, default={})
    extra_data = Column(JSON, default={})

    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    achievements = relationship("Achievement", back_populates="game", cascade="all, delete-orphan")
    price_alerts = relationship("PriceAlert", back_populates="game", cascade="all, delete-orphan")

class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(BigInteger, ForeignKey("games.id"), index=True)
    
    api_name = Column(String)
    category = Column(String, default="base")
    locales = Column(JSON, default={})
    icon_url = Column(String)
    
    is_hidden = Column(Boolean, default=False)
    global_percent = Column(Float, default=0.0)

    game = relationship("Game", back_populates="achievements")

class PriceAlert(Base):
    __tablename__ = "price_alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, index=True)
    game_id = Column(BigInteger, ForeignKey("games.id"))
    target_price = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    game = relationship("Game", back_populates="price_alerts")

# НОВАЯ МОДЕЛЬ ДЛЯ КЭША ЦЕН
class GamePrice(Base):
    __tablename__ = "game_prices"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    game_id = Column(BigInteger, index=True)
    country_code = Column(String, index=True)
    price_fmt = Column(String) # Отформатированная цена (напр. "5 900₸")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())