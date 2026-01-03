from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def get_media_pagination(game_id: int, current_index: int, total_count: int, media_type: str) -> InlineKeyboardMarkup:
    """Кнопки для листания картинок (Верхнее сообщение)"""
    builder = InlineKeyboardBuilder()
    
    if current_index > -1:
        builder.button(text="⬅️", callback_data=f"media_{game_id}_{current_index - 1}")
    
    if current_index == -1:
        label = "Обложка"
        action = "ignore"
    else:
        label = f"Скрин {current_index + 1}/{total_count}"
        action = f"media_{game_id}_-1"

    builder.button(text=f"🖼 {label}", callback_data=action)

    if current_index < total_count - 1:
        builder.button(text="➡️", callback_data=f"media_{game_id}_{current_index + 1}")
    
    width = 1
    if current_index > -1: width += 1
    if current_index < total_count - 1: width += 1
    
    builder.adjust(width)
    return builder.as_markup()

# === ИЗМЕНЕНИЕ ЗДЕСЬ ===
def get_info_pagination(game_id: int, current_page: int, total_pages: int, image_msg_id: int = 0) -> InlineKeyboardMarkup:
    """
    Кнопки для текста.
    image_msg_id: ID сообщения с картинкой, которое висит выше.
    """
    builder = InlineKeyboardBuilder()
    
    # Мы добавляем image_msg_id в callback_data кнопок навигации, 
    # чтобы не потерять его при переключении страниц текста.
    # Формат: info_GAMEID_PAGE_IMGID
    
    if total_pages == 2:
        if current_page == 1:
            builder.button(text="🛠 Требования и Детали ➡️", callback_data=f"info_{game_id}_2_{image_msg_id}")
        else:
            builder.button(text="⬅️ Об игре", callback_data=f"info_{game_id}_1_{image_msg_id}")
    else:
        if current_page > 1:
            builder.button(text="⬅️", callback_data=f"info_{game_id}_{current_page - 1}_{image_msg_id}")
        builder.button(text=f"{current_page}/{total_pages}", callback_data="ignore")
        if current_page < total_pages:
            builder.button(text="➡️", callback_data=f"info_{game_id}_{current_page + 1}_{image_msg_id}")
    
    builder.adjust(1)
    
    row_btns = []
    
    # === ГЛАВНОЕ ИЗМЕНЕНИЕ ===
    # Передаем image_msg_id в кнопку ачивок: ach_GAMEID_INDEX_IMGID
    row_btns.append(
        InlineKeyboardBuilder().button(text="🏆 Ачивки", callback_data=f"ach_{game_id}_0_{image_msg_id}").as_markup().inline_keyboard[0][0]
    )
    
    row_btns.append(
        InlineKeyboardBuilder().button(text="🛒 Steam", url=f"https://store.steampowered.com/app/{game_id}/").as_markup().inline_keyboard[0][0]
    )
    
    builder.row(*row_btns)
    
    return builder.as_markup()