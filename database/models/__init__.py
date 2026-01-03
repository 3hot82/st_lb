from .base import Base
from .game import Game, Achievement, PriceAlert, GamePrice # <--- Добавили GamePrice
from .user import User, UserLibrary

__all__ = [
    "Base",
    "Game",
    "Achievement",
    "PriceAlert",
    "GamePrice", # <--- Добавили сюда
    "User",
    "UserLibrary"
]