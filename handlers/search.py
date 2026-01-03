from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession

from database.repo.games import GameRepo
from keyboards.game_card import get_search_results_kb
from handlers.game_details import send_game_interface 

router = Router()

# --- ХЕНДЛЕРЫ МЕНЮ ---

@router.message(F.text == "🎮 Поиск игр")
async def menu_search_btn(message: types.Message):
    await message.answer("✍️ Просто напиши название игры в чат, и я найду её.\n\n<i>Например: Ведьмак, CS2, Stalker</i>", parse_mode="HTML")

@router.message(F.text == "🎲 Случайная игра")
async def menu_random_btn(message: types.Message, session: AsyncSession):
    repo = GameRepo(session)
    game = await repo.get_random_game()
    if game:
        # ДОБАВЛЕНА SESSION
        await send_game_interface(message, game, session)
    else:
        await message.answer("В базе пока пусто 😔")

@router.message(F.text == "⚙️ Настройки")
async def menu_settings_btn(message: types.Message):
    await message.answer("Настройки пока в разработке 🛠")

# --- ХЕНДЛЕР ПОИСКА ---

@router.message(F.text)
async def search_games(message: types.Message, session: AsyncSession):
    query = message.text.strip()
    
    if query.startswith("/") or len(query) < 2:
        return

    if query in ["👤 Мой профиль", "🎮 Поиск игр", "🎲 Случайная игра", "⚙️ Настройки"]:
        return

    repo = GameRepo(session)
    games = await repo.search(query)

    if not games:
        await message.answer(f"❌ По запросу <b>'{query}'</b> ничего не найдено.", parse_mode="HTML")
        return

    if len(games) == 1:
        # ДОБАВЛЕНА SESSION
        await send_game_interface(message, games[0], session)
    else:
        await message.answer(
            f"🔎 Найдено игр: {len(games)}. Выбери нужную:",
            reply_markup=get_search_results_kb(games)
        )