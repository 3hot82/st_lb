from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from states.user_states import UserStates
from services.steam import steam_service
from database.repo.users import UserRepo
from keyboards.main_menu import get_onboarding_kb

router = Router()

@router.message(F.text == "👤 Мой профиль")
async def my_profile_handler(message: types.Message, state: FSMContext, session: AsyncSession):
    repo = UserRepo(session)
    user = await repo.get_user(message.from_user.id)
    
    if user and user.steam_id:
        # Показываем страну, если она есть, иначе US
        flag = user.country if user.country else "US"
        
        await message.answer(
            f"👤 <b>Твой профиль:</b>\n"
            f"🆔 Steam ID: <code>{user.steam_id}</code>\n"
            f"🌍 Регион цен: <b>{flag}</b>\n"
            f"📅 Дата подключения: {user.created_at.strftime('%d.%m.%Y')}\n\n"
            "Чтобы обновить библиотеку игр, отправь /refresh",
            parse_mode="HTML"
        )
    else:
        # Если не подключен
        await message.answer(
            "🔗 <b>Привязка Steam</b>\n\n"
            "Пришли мне ссылку на твой профиль Steam или твой Steam ID.\n"
            "<i>Пример: https://steamcommunity.com/id/gaben/</i>",
            reply_markup=get_onboarding_kb(),
            parse_mode="HTML"
        )
        await state.set_state(UserStates.waiting_for_steam_link)

@router.message(UserStates.waiting_for_steam_link)
async def process_steam_link(message: types.Message, state: FSMContext, session: AsyncSession):
    input_text = message.text.strip()
    
    # 1. Пытаемся получить ID
    steam_id = await steam_service.resolve_vanity_url(input_text)
    
    if not steam_id:
        await message.answer("❌ Не удалось найти такой профиль. Проверь ссылку.")
        return

    # 2. Проверяем доступность игр (Приватность)
    await message.answer("⏳ Проверяю настройки приватности...")
    games = await steam_service.get_owned_games(steam_id)
    
    if games is None:
        await message.answer(
            "🔒 <b>Профиль скрыт!</b>\n\n"
            "Я не вижу твои игры. Открой их в настройках Steam:\n"
            "<i>Редактировать профиль -> Приватность -> Доступ к играм: Открытый</i>\n\n"
            "После этого пришли ссылку еще раз.",
            parse_mode="HTML"
        )
        return

    # 3. Получаем инфо о юзере (ник, аватар, СТРАНА)
    player_summary = await steam_service.get_player_summary(steam_id)
    username = player_summary.get('personaname', 'Unknown')
    avatar = player_summary.get('avatarfull')
    
    # Получаем код страны (например, KZ, RU, US). 
    # Придет None, если пользователь не указал страну в настройках профиля Steam.
    country = player_summary.get('loccountrycode')

    # 4. Сохраняем в БД
    repo = UserRepo(session)
    await repo.create_or_update(
        telegram_id=message.from_user.id,
        steam_id=int(steam_id),
        username=username,
        avatar=avatar,
        country=country # Передаем страну
    )
    
    # Сохраняем библиотеку
    await repo.update_library(message.from_user.id, games)

    # Формируем текст ответа
    display_country = country if country else "US (по умолчанию)"
    warning_text = ""
    if not country:
        warning_text = "\n⚠️ <i>Я не смог определить твой регион (Steam не отдал эти данные). Цены будут в долларах. Укажи страну в настройках профиля Steam и пришли ссылку снова, чтобы исправить.</i>"

    await state.clear()
    await message.answer(
        f"✅ <b>Успешно!</b>\n"
        f"👤 Ник: {username}\n"
        f"🌍 Регион: {display_country}\n"
        f"🎮 Игр в библиотеке: {len(games)}\n"
        f"{warning_text}\n\n"
        "Теперь я знаю, во что ты играешь!",
        parse_mode="HTML"
    )