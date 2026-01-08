from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from fluent.runtime import FluentLocalization

from database.repo.games import GameRepo
from keyboards.game_card import get_search_results_kb
from handlers.game_details import send_game_interface 
from services.steam_store import search_game_in_steam, fetch_and_save_game

router = Router()

# --- ХЕНДЛЕРЫ МЕНЮ ---

@router.message(F.text.in_({"🎮 Поиск игр", "🎮 Search Games"}))
async def menu_search_btn(message: types.Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("search-prompt"), parse_mode="HTML")

@router.message(F.text.in_({"🎲 Случайная игра", "🎲 Random Game"}))
async def menu_random_btn(message: types.Message, session: AsyncSession, l10n: FluentLocalization):
    repo = GameRepo(session)
    game = await repo.get_random_game()
    if game:
        await send_game_interface(message, game, l10n)
    else:
        await message.answer(l10n.format_value("search-empty"))

# --- ХЕНДЛЕР ПОИСКА ---

@router.message(F.text)
async def search_games(message: types.Message, session: AsyncSession, l10n: FluentLocalization):
    query = message.text.strip()
    
    if query.startswith("/") or len(query) < 2: return
    if query in ["👤 Мой профиль", "🎮 Поиск игр", "🎲 Случайная игра", "⚙️ Настройки", 
                 "👤 My Profile", "🎮 Search Games", "🎲 Random Game", "⚙️ Settings"]: return

    repo = GameRepo(session)
    
    # 1. Ищем в локальной БД
    games = await repo.search(query)

    if games:
        # Проверяем на ТОЧНОЕ совпадение
        # Если мы искали "Helldivers 2", а нашли "Helldivers", это НЕ точное совпадение.
        exact_match = None
        for g in games:
            if g.name.lower().strip() == query.lower():
                exact_match = g
                break
        
        # Если нашли ровно одну игру И название совпадает точь-в-точь — открываем
        if len(games) == 1 and exact_match:
            await send_game_interface(message, games[0], l10n)
            return

        # Иначе показываем список + кнопку "Искать в Steam"
        # (Даже если игра одна, но название отличается, лучше дать выбор)
        await message.answer(
            l10n.format_value("search-found", {"count": len(games)}),
            reply_markup=get_search_results_kb(games, query, l10n)
        )
        return

    # 2. Если в базе пусто — сразу ищем в Steam
    await start_steam_search(message, query, session, l10n)


# --- НОВЫЙ ХЕНДЛЕР: ПРИНУДИТЕЛЬНЫЙ ПОИСК В STEAM ---
@router.callback_query(F.data.startswith("force_steam_"))
async def callback_force_steam(callback: types.CallbackQuery, session: AsyncSession, l10n: FluentLocalization):
    # data: force_steam_QUERY
    # split(..., 1) чтобы не ломалось, если в запросе есть подчеркивания
    parts = callback.data.split("_", 2)
    if len(parts) < 3: return
    
    query = parts[2]
    
    # Удаляем старое сообщение с кнопками
    await callback.message.delete()
    
    # Запускаем поиск
    await start_steam_search(callback.message, query, session, l10n)


# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ---
async def start_steam_search(message: types.Message, query: str, session: AsyncSession, l10n: FluentLocalization):
    """Общая логика поиска в Steam и сохранения"""
    status_msg = await message.answer(l10n.format_value("search-searching-steam"))
    
    steam_app_id = await search_game_in_steam(query)
    
    if not steam_app_id:
        await status_msg.edit_text(
            l10n.format_value("search-not-found", {"query": query}),
            parse_mode="HTML"
        )
        return

    await status_msg.edit_text(l10n.format_value("search-downloading"))
    
    new_game = await fetch_and_save_game(session, steam_app_id)
    
    if new_game:
        await status_msg.delete()
        await send_game_interface(message, new_game, l10n)
    else:
        await status_msg.edit_text(l10n.format_value("search-steam-error"))