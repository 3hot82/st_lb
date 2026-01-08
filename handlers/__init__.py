# Файл: steam_bot/handlers/__init__.py

from aiogram import Router
from . import base, onboarding, search, game_details, achievements, settings

def get_handlers_router() -> Router:
    router = Router()
    
    # 1. Сначала проверяем конкретные кнопки и команды
    router.include_router(settings.router)      # <--- ПОДНЯЛИ НАВЕРХ (чтобы кнопка работала)
    router.include_router(base.router)
    router.include_router(onboarding.router)
    
    # 2. Потом обработчики callback-ов (кнопок под сообщениями)
    router.include_router(game_details.router)
    router.include_router(achievements.router)
    
    # 3. В САМОМ КОНЦЕ - поиск
    # Он ловит любой текст, который не подошел под фильтры выше
    router.include_router(search.router)        # <--- ОПУСТИЛИ ВНИЗ
    
    return router