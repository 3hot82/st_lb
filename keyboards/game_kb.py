from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from fluent.runtime import FluentLocalization

def get_game_main_kb(l10n: FluentLocalization, game_id: int, page: int, has_achievements: bool) -> InlineKeyboardMarkup:
    """
    Основная клавиатура под текстом игры.
    page 1: [Store][Achievs] / [Trailers] / [Go to Reqs ->]
    page 2: [<- Back to Info]
    """
    builder = InlineKeyboardBuilder()

    # === СТРАНИЦА 1 (ОСНОВНАЯ) ===
    if page == 1:
        # Ряд 1: Магазин + Ачивки (если есть)
        builder.button(text=l10n.format_value("btn-store"), url=f"https://store.steampowered.com/app/{game_id}/")
        
        if has_achievements:
            builder.button(text=l10n.format_value("btn-achievements"), callback_data=f"achievements_{game_id}_page_1")
        
        # Ряд 2: Трейлеры
        builder.button(text=l10n.format_value("btn-trailers"), callback_data=f"trailers_{game_id}")
        
        # Ряд 3: Кнопка перехода к ТРЕБОВАНИЯМ
        builder.button(text=l10n.format_value("btn-to-reqs"), callback_data=f"info_{game_id}_2")
        
        # Сетка кнопок:
        # Если есть ачивки: [2 кнопки], [1 кнопка], [1 кнопка]
        # Если нет ачивок:  [1 кнопка], [1 кнопка], [1 кнопка]
        if has_achievements:
            builder.adjust(2, 1, 1)
        else:
            builder.adjust(1, 1, 1)

    # === СТРАНИЦА 2 (ТРЕБОВАНИЯ) ===
    elif page == 2:
        # Здесь оставляем только кнопку возврата, чтобы не загромождать экран
        # (Или можно продублировать кнопку магазина, если хотите)
        
        builder.button(text=l10n.format_value("btn-to-info"), callback_data=f"info_{game_id}_1")
        builder.adjust(1)
        
    return builder.as_markup()