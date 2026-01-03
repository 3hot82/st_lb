from aiogram import Router, types, F
from aiogram.types import InputMediaPhoto
from aiogram.enums import ContentType, ParseMode
from sqlalchemy.ext.asyncio import AsyncSession

from database.repo.games import GameRepo
from keyboards.achievements import get_achievements_pagination
from services.game_sync import sync_game_achievements # <--- Импортируем наш новый сервис

router = Router()

@router.callback_query(F.data.startswith("ach_"))
async def achievement_navigation(callback: types.CallbackQuery, session: AsyncSession):
    # data: ach_GAMEID_INDEX_IMGID
    parts = callback.data.split("_")
    game_id = int(parts[1])
    index = int(parts[2])
    image_msg_id = int(parts[3]) if len(parts) > 3 else 0
    
    repo = GameRepo(session)
    
    # 1. Пробуем получить ачивки из базы
    achievements = await repo.get_achievements(game_id)
    
    # 2. Если в базе пусто — пробуем загрузить из Steam
    if not achievements:
        # Показываем уведомление (Toast), чтобы юзер не скучал
        await callback.answer("⏳ Ачивки не найдены. Загружаю из Steam...", show_alert=False)
        
        # Запускаем синхронизацию
        success = await sync_game_achievements(session, game_id)
        
        if success:
            # Если успешно, запрашиваем список снова
            achievements = await repo.get_achievements(game_id)
        else:
            return await callback.answer("❌ У этой игры нет ачивок или ошибка Steam.", show_alert=True)

    # Если после загрузки все равно пусто (странно, но бывает)
    if not achievements:
        return await callback.answer("Список ачивок пуст.", show_alert=True)

    total = len(achievements)
    if index < 0: index = 0
    if index >= total: index = total - 1
    
    ach = achievements[index]
    
    # --- ФОРМИРОВАНИЕ ТЕКСТА (как раньше) ---
    locales = ach.locales or {}
    ru_data = locales.get('ru') or {}
    en_data = locales.get('en') or {}
    name = ru_data.get('name') or en_data.get('name') or ach.api_name
    
    raw_desc = ru_data.get('desc') or en_data.get('desc')
    if raw_desc: desc = raw_desc
    elif ach.is_hidden: desc = "🔒 <i>Это скрытое достижение. Подробности раскрываются по ходу игры.</i>"
    else: desc = "Описание отсутствует."
    
    percent = ach.global_percent
    rarity_emoji = "🟢"
    rarity_text = "Обычная"
    if percent < 10: 
        rarity_emoji = "🔴"
        rarity_text = "Легендарная"
    elif percent < 30: 
        rarity_emoji = "🟡"
        rarity_text = "Редкая"
    
    caption = (
        f"🏆 <b>{name}</b>\n\n"
        f"{desc}\n\n"
        f"📊 {rarity_text}: {rarity_emoji} <b>{percent}%</b> игроков"
    )
    
    keyboard = get_achievements_pagination(game_id, index, total)
    
    # --- ОТПРАВКА ---
    
    if callback.message.content_type == ContentType.TEXT:
        # Вход в режим ачивок
        await callback.message.delete()
        
        # Удаляем картинку игры, если она висит выше
        if image_msg_id > 0:
            try:
                await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=image_msg_id)
            except Exception:
                pass 
        
        await callback.message.answer_photo(
            photo=ach.icon_url,
            caption=caption,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    else:
        # Листание
        media = InputMediaPhoto(media=ach.icon_url, caption=caption, parse_mode=ParseMode.HTML)
        try:
            await callback.message.edit_media(media=media, reply_markup=keyboard)
        except Exception:
            await callback.answer()