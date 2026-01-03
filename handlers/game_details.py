import logging
import re
import datetime
from aiogram import Router, types, F
from aiogram.types import InputMediaPhoto, InputMediaVideo
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from database.repo.games import GameRepo
from database.repo.users import UserRepo
from database.models.game import GamePrice
from services.steam import steam_service
from keyboards.pagination import get_media_pagination, get_info_pagination

router = Router()

# === ЛОГИКА ЦЕН ===
async def get_actual_price(session: AsyncSession, game_id: int, user_id: int) -> str:
    user_repo = UserRepo(session)
    user = await user_repo.get_user(user_id)
    country = user.country if (user and user.country) else "US"
    
    stmt = select(GamePrice).where(GamePrice.game_id == game_id, GamePrice.country_code == country)
    result = await session.execute(stmt)
    cached = result.scalars().first()
    
    now = datetime.datetime.now(datetime.timezone.utc)
    
    if cached and cached.updated_at:
        last = cached.updated_at.replace(tzinfo=datetime.timezone.utc) if cached.updated_at.tzinfo is None else cached.updated_at
        if (now - last).total_seconds() < 86400:
            return cached.price_fmt

    new_price = await steam_service.get_game_price(game_id, country)
    if new_price:
        stmt = insert(GamePrice).values(game_id=game_id, country_code=country, price_fmt=new_price, updated_at=now)\
            .on_conflict_do_update(index_elements=['game_id', 'country_code'], set_={"price_fmt": new_price, "updated_at": now})
        await session.execute(stmt)
        await session.commit()
        return new_price
    
    return cached.price_fmt if cached else None

# === ОТПРАВКА ИНТЕРФЕЙСА ===

async def send_game_interface(message: types.Message, game, session: AsyncSession):
    # 1. Данные
    locales = game.locales or {}
    extra_data = game.extra_data or {}
    ru_data = locales.get('ru') or {}
    en_data = locales.get('en') or {}
    
    header_url = ru_data.get('header_image') or en_data.get('header_image') or extra_data.get('header_image')
    if not header_url: header_url = "https://via.placeholder.com/460x215?text=No+Image"

    screenshots = extra_data.get('screenshots') or []
    movies = extra_data.get('movies') or []
    total_media = len(screenshots) + len(movies)

    media_kb = get_media_pagination(game.id, -1, total_media, "image")
    
    # 2. Отправляем ФОТО (Обложка всегда с подписью названия игры)
    img_msg = None
    try:
        img_msg = await message.answer_photo(
            photo=header_url,
            caption=f"🖼 <b>{game.name}</b>", # <--- ПОДПИСЬ ИГРЫ
            reply_markup=media_kb,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Error sending photo: {e}")
        await message.answer("Не удалось загрузить фото.")

    # 3. Текст
    custom_price = await get_actual_price(session, game.id, message.chat.id)
    info_text = get_page_text(game, 1, custom_price)
    
    image_msg_id = img_msg.message_id if img_msg else 0
    info_kb = get_info_pagination(game.id, 1, 2, image_msg_id) 
    
    await message.answer(
        text=info_text,
        reply_markup=info_kb,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

# === ГЕНЕРАТОР ТЕКСТА ===
def get_page_text(game, page: int, custom_price: str = None) -> str:
    locales = game.locales or {}
    extra_data = game.extra_data or {}
    ru_data = locales.get('ru') or {}
    en_data = locales.get('en') or {}
    
    desc = ru_data.get('short_desc') or en_data.get('short_desc') or "Описание отсутствует."
    
    if custom_price: price_str = custom_price
    else:
        if game.is_free: price_str = "Free"
        elif game.price_current:
            val = game.price_current
            price_str = f"{int(val)}$" if val.is_integer() else f"{val}$"
        else: price_str = "—"

    release = game.release_date or "TBA"
    year_match = re.search(r'\d{4}', release)
    if year_match: release = year_match.group(0)

    time_str = f"{int(game.time_main)} ч." if game.time_main else "—"
    meta = f"{game.metacritic_score}" if game.metacritic_score else "—"
    
    if page == 1:
        return (
            f"🎮 <b>{game.name}</b>\n"
            f"⭐️ <b>{meta}</b>      ⏱ <b>{time_str}</b>\n\n"
            f"{desc}\n\n"
            f"📅 {release}    💰 <b>{price_str}</b>\n"
            f"➖➖➖➖➖➖➖\n"
            f"🏆 Ачивок: <b>{game.achievements_count}</b>   👥 Отзывов: <b>{game.reviews_total:,}</b>".replace(',', ' ')
        )
    
    elif page == 2:
        devs = ", ".join(extra_data.get('developers') or ["Неизвестно"])
        pubs = ", ".join(extra_data.get('publishers') or ["Неизвестно"])
        reqs = extra_data.get('pc_requirements') or {}
        if isinstance(reqs, list): reqs = {}
        min_req = re.sub(r'<[^>]+>', '', str(reqs.get('minimum', 'Не указаны'))).replace("Minimum:", "").strip()
        if len(min_req) > 500: min_req = min_req[:500] + "..."

        return (
            f"🛠 <b>Системные требования:</b>\n"
            f"<code>{min_req}</code>\n\n"
            f"👨‍💻 <b>Разработчик:</b> {devs}\n"
            f"📢 <b>Издатель:</b> {pubs}\n"
            f"🆔 <b>AppID:</b> <code>{game.id}</code>"
        )
    return "Error"

# === ХЕНДЛЕРЫ ===

@router.callback_query(F.data.startswith("media_"))
async def callback_media(callback: types.CallbackQuery, session: AsyncSession):
    parts = callback.data.split("_")
    game_id = int(parts[1])
    index = int(parts[2])
    
    repo = GameRepo(session)
    game = await repo.get_by_id(game_id)
    if not game: return

    locales = game.locales or {}
    extra_data = game.extra_data or {}
    ru_data = locales.get('ru') or {}
    en_data = locales.get('en') or {}
    screenshots = extra_data.get('screenshots') or []
    movies = extra_data.get('movies') or []
    total = len(screenshots) + len(movies)

    # Корректировка индекса
    if index >= total and total > 0:
        index = total - 1

    media_obj = None
    current_url = ""
    
    # === НАСТРОЙКА ПОДПИСИ ===
    if index == -1:
        # Обложка: Название игры
        caption = f"🖼 <b>{game.name}</b>"
    else:
        # Скриншоты/Видео: БЕЗ подписи
        caption = None 

    # 1. ОБЛОЖКА
    if index == -1:
        url = ru_data.get('header_image') or en_data.get('header_image') or extra_data.get('header_image')
        if not url: url = "https://via.placeholder.com/460x215?text=No+Image"
        current_url = url
        media_obj = InputMediaPhoto(media=url, caption=caption, parse_mode=ParseMode.HTML)
    
    # 2. СКРИНШОТ
    elif 0 <= index < len(screenshots):
        current_url = screenshots[index]
        media_obj = InputMediaPhoto(media=current_url, caption=caption, parse_mode=ParseMode.HTML)
    
    # 3. ВИДЕО
    elif index >= len(screenshots):
        vid_index = index - len(screenshots)
        if vid_index < len(movies):
            current_url = movies[vid_index]
            media_obj = InputMediaVideo(media=current_url, caption=caption, parse_mode=ParseMode.HTML)

    if media_obj:
        try:
            kb = get_media_pagination(game_id, index, total, "mixed")
            await callback.message.edit_media(media=media_obj, reply_markup=kb)
        except Exception as e:
            # === САМООЧИСТКА ===
            logging.error(f"❌ Битый файл обнаружен: {current_url}. Ошибка: {e}")
            
            deleted = await repo.delete_broken_media(game_id, current_url)
            
            if deleted:
                await callback.answer("⚠️ Файл поврежден. Исправляю...", show_alert=False)
                
                new_total = total - 1
                if index >= new_total and index > -1:
                    index = index - 1
                
                # Используем model_copy для рекурсии
                new_callback = callback.model_copy(update={"data": f"media_{game_id}_{index}"})
                await callback_media(new_callback, session)
            else:
                await callback.answer("Ошибка загрузки.", show_alert=True)
            
    else:
        if index != -1:
             new_callback = callback.model_copy(update={"data": f"media_{game_id}_-1"})
             await callback_media(new_callback, session)

@router.callback_query(F.data.startswith("info_"))
async def callback_info(callback: types.CallbackQuery, session: AsyncSession):
    parts = callback.data.split("_")
    game_id = int(parts[1])
    page = int(parts[2])
    image_msg_id = int(parts[3]) if len(parts) > 3 else 0
    
    repo = GameRepo(session)
    game = await repo.get_by_id(game_id)
    if not game: return

    custom_price = await get_actual_price(session, game.id, callback.message.chat.id)
    text = get_page_text(game, page, custom_price)
    
    kb = get_info_pagination(game.id, page, 2, image_msg_id)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception:
        await callback.answer()

@router.callback_query(F.data.startswith("view_game_"))
async def callback_view_game_entry(callback: types.CallbackQuery, session: AsyncSession):
    game_id = int(callback.data.split("_")[2])
    repo = GameRepo(session)
    game = await repo.get_by_id(game_id)
    
    if game:
        await callback.message.delete()
        await send_game_interface(callback.message, game, session)
    else:
        await callback.answer("Игра не найдена.")