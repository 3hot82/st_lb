from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from fluent.runtime import FluentLocalization

def get_game_card_kb(l10n: FluentLocalization, game_id: int, has_achievements: bool, has_ru_locale: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # 1. Ссылка на магазин
    builder.button(text=l10n.format_value("game-store-btn"), url=f"https://store.steampowered.com/app/{game_id}/")
    
    # 2. Ачивки
    if has_achievements:
        builder.button(text=l10n.format_value("game-achievements-btn"), callback_data=f"achievements_{game_id}_page_1")
    
    # 3. Трейлеры
    builder.button(text=l10n.format_value("game-trailers-btn"), callback_data=f"trailers_{game_id}")
    
    # 4. Если нет русского описания
    if not has_ru_locale:
        builder.button(text=l10n.format_value("game-update-ru-btn"), callback_data=f"update_ru_{game_id}")

    builder.adjust(1, 2)
    return builder.as_markup()

def get_search_results_kb(games: list, query: str = "", l10n: FluentLocalization = None) -> InlineKeyboardMarkup:
    """
    Генерирует список кнопок с найденными играми.
    Если передан query и l10n, добавляет кнопку принудительного поиска в Steam.
    """
    builder = InlineKeyboardBuilder()
    
    # Кнопки с играми из базы
    for game in games:
        builder.button(text=f"🎮 {game.name}", callback_data=f"view_game_{game.id}")
    
    # Если передан запрос — добавляем кнопку "Искать в Steam"
    if query and l10n:
        # Обрезаем запрос, чтобы влезть в лимит callback_data (64 байта)
        # force_steam_ (12 chars) + query (max ~40 chars)
        short_query = query[:40]
        
        btn_text = l10n.format_value("search-force-steam")
        # Если ключа нет в словаре, будет "search-force-steam", ставим дефолт
        if btn_text == "search-force-steam": 
            btn_text = "☁️ Steam Search"
            
        builder.button(text=btn_text, callback_data=f"force_steam_{short_query}")
    
    builder.adjust(1)
    return builder.as_markup()