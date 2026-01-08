from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ContentType, ParseMode # <--- Важные импорты
from sqlalchemy.ext.asyncio import AsyncSession
from fluent.runtime import FluentLocalization

from database.repo.games import GameRepo

router = Router()

@router.callback_query(F.data.startswith("achievements_"))
async def show_achievements(callback: types.CallbackQuery, session: AsyncSession, l10n: FluentLocalization):
    # Формат data: achievements_{game_id}_page_{page}
    parts = callback.data.split("_")
    game_id = int(parts[1])
    
    # Логика определения страницы
    if "page" in parts[2]:
        page_num = int(parts[3])
        page = page_num
    else:
        page = 1

    repo = GameRepo(session)
    
    # 1. Считаем количество
    total_count = await repo.count_achievements(game_id)
    
    if total_count == 0:
        await callback.answer(l10n.format_value("ach-empty"), show_alert=True)
        return

    # Индекс текущей ачивки
    current_index = page - 1
    if current_index < 0: current_index = 0
    if current_index >= total_count: current_index = total_count - 1
    
    # 2. Получаем ОДНУ ачивку
    ach_list = await repo.get_achievements(game_id, page=current_index+1, limit=1)
    
    if not ach_list:
        await callback.answer("Ошибка загрузки")
        return
        
    ach = ach_list[0]

    # 3. Формируем текст
    locales = ach.locales or {}
    user_lang = l10n.locales[0]
    ach_data = locales.get(user_lang) or locales.get('en') or locales.get('ru') or {}
    
    name = ach_data.get('displayName') or ach.api_name
    raw_desc = ach_data.get('description')
    
    if raw_desc:
        desc = raw_desc
    elif ach.is_hidden:
        desc = l10n.format_value("ach-locked-desc")
    else:
        desc = l10n.format_value("ach-no-desc")
    
    percent = ach.global_percent
    if percent < 10:
        rarity_text = l10n.format_value("ach-rarity-legendary")
    elif percent < 30:
        rarity_text = l10n.format_value("ach-rarity-rare")
    else:
        rarity_text = l10n.format_value("ach-rarity-common")
    
    caption = (
        f"🏆 <b>{name}</b>\n\n"
        f"{desc}\n\n"
        f"📊 {rarity_text} <b>{percent:.1f}%</b> {l10n.format_value('ach-players')}"
    )

    # 4. Клавиатура
    builder = InlineKeyboardBuilder()
    
    if current_index > 0:
        builder.button(text="⬅️", callback_data=f"achievements_{game_id}_page_{current_index}")
    
    builder.button(text=f"{current_index + 1} / {total_count}", callback_data="ignore")

    if current_index < total_count - 1:
        builder.button(text="➡️", callback_data=f"achievements_{game_id}_page_{current_index + 2}")
    
    builder.adjust(3)
    
    # Кнопка ВОЗВРАТА (view_game_ удалит ачивку и вернет игру)
    builder.row(
        types.InlineKeyboardButton(text=l10n.format_value("btn-back-to-game"), callback_data=f"view_game_{game_id}")
    )
    
    # 5. ОТПРАВКА И УДАЛЕНИЕ СТАРОГО
    
    # Если мы пришли из текстового меню (нажали кнопку "Ачивки" под игрой)
    if callback.message.content_type == ContentType.TEXT:
        # 1. Удаляем сообщение с кнопками (текст игры)
        await callback.message.delete()
        
        # 2. !!! ВАЖНО: Пытаемся удалить сообщение с картинкой выше !!!
        # Обычно оно имеет ID на 1 меньше текущего
        try:
            prev_msg_id = callback.message.message_id - 1
            await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=prev_msg_id)
        except Exception:
            # Если не получилось (например, юзер удалил сам), игнорируем
            pass
        
        # 3. Отправляем ачивку (Фото + Текст одним сообщением)
        await callback.message.answer_photo(
            photo=ach.icon_url,
            caption=caption,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        
    # Если мы уже листаем ачивки (там уже фото) -> просто редактируем
    else:
        media = types.InputMediaPhoto(media=ach.icon_url, caption=caption, parse_mode=ParseMode.HTML)
        try:
            await callback.message.edit_media(media=media, reply_markup=builder.as_markup())
        except Exception:
            await callback.answer()