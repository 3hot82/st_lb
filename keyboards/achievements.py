from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def get_achievements_pagination(game_id: int, current_index: int, total_count: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # 1. Кнопка Назад (или в конец, если мы в начале)
    if current_index > 0:
        builder.button(text="⬅️", callback_data=f"ach_{game_id}_{current_index - 1}")
    else:
        builder.button(text="🔚", callback_data=f"ach_{game_id}_{total_count - 1}")

    # 2. Индикатор
    builder.button(text=f"{current_index + 1}/{total_count}", callback_data="ignore")

    # 3. Кнопка Вперед (или в начало, если мы в конце)
    if current_index < total_count - 1:
        builder.button(text="➡️", callback_data=f"ach_{game_id}_{current_index + 1}")
    else:
        builder.button(text="🔄", callback_data=f"ach_{game_id}_0")
    
    builder.adjust(3)
    
    # 4. Кнопка возврата к карточке игры
    builder.row(
        # Эта кнопка вызовет view_game_, который вернет стандартный интерфейс игры
        InlineKeyboardBuilder().button(text="🔙 К карточке игры", callback_data=f"view_game_{game_id}").as_markup().inline_keyboard[0][0]
    )
    
    return builder.as_markup()