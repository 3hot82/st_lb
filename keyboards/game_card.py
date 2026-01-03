# Файл: steam_bot/keyboards/game_card.py

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def get_game_card_kb(game_id: int, has_achievements: bool, has_ru_locale: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # 1. Ссылка на магазин (всегда полезна)
    builder.button(text="🛒 Steam Store", url=f"https://store.steampowered.com/app/{game_id}/")
    
    # 2. Ачивки (если они есть)
    if has_achievements:
        builder.button(text="🏆 Ачивки", callback_data=f"achievements_{game_id}_page_1")
    
    # 3. Трейлеры (если есть в базе, но кнопку оставим всегда)
    builder.button(text="📹 Трейлеры", callback_data=f"trailers_{game_id}")
    
    # 4. Если нет русского описания - кнопка обновить
    if not has_ru_locale:
        builder.button(text="🇷🇺 Загрузить RU", callback_data=f"update_ru_{game_id}")

    # Красивая сетка: 1 кнопка (магазин), потом по 2 в ряд
    builder.adjust(1, 2)
    return builder.as_markup()

def get_search_results_kb(games: list) -> InlineKeyboardMarkup:
    """Генерирует список кнопок с найденными играми"""
    builder = InlineKeyboardBuilder()
    for game in games:
        # В callback_data кладем ID игры
        builder.button(text=f"🎮 {game.name}", callback_data=f"view_game_{game.id}")
    
    builder.adjust(1)
    return builder.as_markup()