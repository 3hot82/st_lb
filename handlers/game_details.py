import logging
import re
from aiogram import Router, types, F
from aiogram.types import InputMediaPhoto, InputMediaVideo
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from fluent.runtime import FluentLocalization

from database.repo.games import GameRepo
from keyboards.pagination import get_media_pagination
from keyboards.game_kb import get_game_main_kb 

router = Router()

# === ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ===
def clean_steam_html(raw_html: str) -> str:
    """Удаляет HTML теги, которые ломают Телеграм."""
    if not raw_html: return ""
    text = str(raw_html).replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    clean_regex = re.compile('<.*?>')
    text = re.sub(clean_regex, '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

# === ЛОГИКА ОТОБРАЖЕНИЯ (Первое сообщение) ===

async def send_game_interface(message: types.Message, game, l10n: FluentLocalization):
    locales = game.locales or {}
    extra_data = game.extra_data or {}
    ru_data = locales.get('ru') or {}
    en_data = locales.get('en') or {}

    # 1. МЕДИА (Обложка)
    header_url = ru_data.get('header_image') or \
                 en_data.get('header_image') or \
                 extra_data.get('header_image')

    if not header_url:
        header_url = "https://via.placeholder.com/600x350?text=No+Image"

    screenshots = extra_data.get('screenshots', [])
    movies = extra_data.get('movies', [])
    total_media = len(screenshots) + len(movies)

    # На обложке только кнопка [➡️]
    media_kb = get_media_pagination(l10n, game.id, -1, total_media, "image")
    
    try:
        await message.answer_photo(
            photo=header_url,
            caption=f"🎮 <b>{game.name}</b>",
            reply_markup=media_kb,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Photo error: {e}")
        await message.answer(f"🎮 <b>{game.name}</b>", parse_mode=ParseMode.HTML)

    # 2. ТЕКСТ (Страница 1)
    info_text = get_page_text(game, 1, l10n)
    has_achievs = game.achievements_count > 0
    
    # Клавиатура действий
    info_kb = get_game_main_kb(l10n, game.id, 1, has_achievs)
    
    await message.answer(
        text=info_text,
        reply_markup=info_kb,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )

# === ГЕНЕРАТОР ТЕКСТА ===

def get_page_text(game, page: int, l10n: FluentLocalization) -> str:
    locales = game.locales or {}
    extra_data = game.extra_data or {}
    content_data = locales.get('ru') or locales.get('en') or {}
    
    if page == 1:
        price = f"{game.price_current} $" if game.price_current else "Free"
        time_str = f"{int(game.time_100)} h." if game.time_100 else "—"
        meta = str(game.metacritic_score) if game.metacritic_score else "—"
        date = game.release_date[:4] if (game.release_date and len(game.release_date) >= 4) else "—"
        desc = clean_steam_html(content_data.get('short_desc') or "")
        reviews = f"{game.reviews_total:,}".replace(",", " ")
        devs = ", ".join(extra_data.get('developers') or []) or "—"

        return l10n.format_value("game-info-header", {
            "name": game.name, "meta": meta, "time": time_str, "desc": desc,
            "date": date, "price": price, "achievements": game.achievements_count,
            "reviews": reviews, "devs": devs
        })
    elif page == 2:
        reqs = extra_data.get('pc_requirements') or {}
        raw_reqs = "Не указаны" if isinstance(reqs, list) else (reqs.get('minimum') or "Не указаны")
        return l10n.format_value("game-reqs-header", {"reqs": clean_steam_html(raw_reqs)[:900]})
    return "Error"

# === ХЕНДЛЕРЫ МЕДИА ===

@router.callback_query(F.data.startswith("media_"))
async def callback_media(callback: types.CallbackQuery, session: AsyncSession, l10n: FluentLocalization):
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
    screenshots = extra_data.get('screenshots', [])
    movies = extra_data.get('movies', [])
    total = len(screenshots) + len(movies)

    media_obj = None
    if index == -1:
        url = ru_data.get('header_image') or en_data.get('header_image') or extra_data.get('header_image') or "https://via.placeholder.com/600x350"
        media_obj = InputMediaPhoto(media=url, caption=f"🎮 <b>{game.name}</b>", parse_mode=ParseMode.HTML)
    elif 0 <= index < len(screenshots):
        url = screenshots[index]
        media_obj = InputMediaPhoto(media=url, caption=None)
    elif index >= len(screenshots):
        vid_index = index - len(screenshots)
        url = movies[vid_index]
        media_obj = InputMediaVideo(media=url, caption=None)

    try:
        kb = get_media_pagination(l10n, game_id, index, total, "mixed")
        await callback.message.edit_media(media=media_obj, reply_markup=kb)
    except Exception:
        await callback.answer()

# === НОВЫЙ ХЕНДЛЕР: ТРЕЙЛЕРЫ ===
@router.callback_query(F.data.startswith("trailers_"))
async def callback_trailers(callback: types.CallbackQuery, session: AsyncSession, l10n: FluentLocalization):
    game_id = int(callback.data.split("_")[1])
    repo = GameRepo(session)
    game = await repo.get_by_id(game_id)
    if not game: return

    extra_data = game.extra_data or {}
    screenshots = extra_data.get('screenshots', [])
    movies = extra_data.get('movies', [])
    
    if not movies:
        await callback.answer("Трейлеров нет 😔", show_alert=True)
        return

    # Индекс первого видео идет сразу после скриншотов
    first_video_index = len(screenshots)
    total_media = len(screenshots) + len(movies)
    
    video_url = movies[0]
    
    media_obj = InputMediaVideo(media=video_url, caption=None)
    kb = get_media_pagination(l10n, game_id, first_video_index, total_media, "video")
    
    try:
        await callback.message.edit_media(media=media_obj, reply_markup=kb)
        await callback.answer()
    except Exception as e:
        logging.error(f"Trailer error: {e}")
        await callback.answer("Не удалось загрузить видео")

# === ХЕНДЛЕРЫ ТЕКСТА ===

@router.callback_query(F.data.startswith("info_"))
async def callback_info(callback: types.CallbackQuery, session: AsyncSession, l10n: FluentLocalization):
    parts = callback.data.split("_")
    game_id = int(parts[1])
    page = int(parts[2])
    repo = GameRepo(session)
    game = await repo.get_by_id(game_id)
    if not game: return

    text = get_page_text(game, page, l10n)
    has_achievs = game.achievements_count > 0
    kb = get_game_main_kb(l10n, game_id, page, has_achievs)
    
    try:
        await callback.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception:
        await callback.answer()

@router.callback_query(F.data.startswith("view_game_"))
async def callback_view_game_entry(callback: types.CallbackQuery, session: AsyncSession, l10n: FluentLocalization):
    game_id = int(callback.data.split("_")[2])
    repo = GameRepo(session)
    game = await repo.get_by_id(game_id)
    if game:
        await callback.message.delete()
        await send_game_interface(callback.message, game, l10n)
    else:
        await callback.answer(l10n.format_value("search-not-found", {"query": str(game_id)}))