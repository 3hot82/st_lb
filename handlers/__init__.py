# Файл: steam_bot/handlers/__init__.py

from aiogram import Router
from . import base, onboarding, search, game_details, achievements # <--- Добавили achievements

def get_handlers_router() -> Router:
    router = Router()
    
    # Порядок важен (хотя тут не критично)
    router.include_router(base.router)
    router.include_router(onboarding.router)
    router.include_router(search.router)
    router.include_router(game_details.router)
    router.include_router(achievements.router) # <--- Подключили
    
    return router