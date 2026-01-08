from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from fluent.runtime import FluentLocalization

def get_media_pagination(l10n: FluentLocalization, game_id: int, current_index: int, total_count: int, media_type: str) -> InlineKeyboardMarkup:
    """
    Кнопки для листания медиа (Скриншоты/Видео).
    
    current_index:
      -1 = Обложка (Cover)
       0..N = Скриншоты
    """
    builder = InlineKeyboardBuilder()
    
    # === СЦЕНАРИЙ 1: МЫ НА ОБЛОЖКЕ ===
    if current_index == -1:
        # Показываем кнопку "Вперед", только если есть скриншоты
        if total_count > 0:
            builder.button(text="➡️", callback_data=f"media_{game_id}_0")
        
        # Кнопок в ряду: 1
        builder.adjust(1)

    # === СЦЕНАРИЙ 2: МЫ СМОТРИМ СКРИНШОТЫ ===
    else:
        # 1. Кнопка НАЗАД
        # Если current_index = 0, то (0 - 1) = -1 (вернет на обложку)
        builder.button(text="⬅️", callback_data=f"media_{game_id}_{current_index - 1}")
        
        # 2. Кнопка СЧЕТЧИК (При нажатии возвращает на обложку)
        builder.button(
            text=f"{current_index + 1}/{total_count}", 
            callback_data=f"media_{game_id}_-1" # -1 ведет на обложку
        )

        # 3. Кнопка ВПЕРЕД
        if current_index < total_count - 1:
            builder.button(text="➡️", callback_data=f"media_{game_id}_{current_index + 1}")
        
        # Выравнивание: 3 кнопки в ряд (или 2, если это последний слайд)
        builder.adjust(3)
    
    return builder.as_markup()

def get_info_pagination(game_id: int, current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    """
    Кнопки для листания страниц текста (Инфо <-> Требования).
    """
    builder = InlineKeyboardBuilder()
    
    # Навигация страниц
    if current_page > 1:
        builder.button(text="⬅️", callback_data=f"info_{game_id}_{current_page - 1}")
    
    builder.button(text=f"📄 {current_page}/{total_pages}", callback_data="ignore")
    
    if current_page < total_pages:
        builder.button(text="➡️", callback_data=f"info_{game_id}_{current_page + 1}")
    
    return builder.as_markup()

def get_achievements_pagination(l10n: FluentLocalization, game_id: int, current_index: int, total_count: int) -> InlineKeyboardMarkup:
    """
    Кнопки для листания ачивок (Галерея).
    """
    builder = InlineKeyboardBuilder()
    
    # Ряд 1: Навигация [⬅️] [X / N] [➡️]
    
    # Кнопка НАЗАД
    if current_index > 0:
        builder.button(text="⬅️", callback_data=f"achievements_{game_id}_{current_index - 1}")
    
    # Счетчик (просто текст)
    builder.button(text=f"{current_index + 1} / {total_count}", callback_data="ignore")

    # Кнопка ВПЕРЕД
    if current_index < total_count - 1:
        builder.button(text="➡️", callback_data=f"achievements_{game_id}_{current_index + 1}")
    
    # Выравниваем первый ряд (3 кнопки)
    builder.adjust(3)
    
    # Ряд 2: Кнопка возврата к игре (на всю ширину)
    builder.row(
        InlineKeyboardButton(
            text=l10n.format_value("btn-back-to-game"), 
            callback_data=f"info_{game_id}_1"
        )
    )
    
    return builder.as_markup()