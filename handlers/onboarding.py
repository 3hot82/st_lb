from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from fluent.runtime import FluentLocalization

from states.user_states import UserStates
from services.steam import steam_service
from database.repo.users import UserRepo
from keyboards.main_menu import get_onboarding_kb

router = Router()

# TODO: В будущем заменить F.text на фильтр по ключу локализации
@router.message(F.text.in_({"👤 Мой профиль", "👤 My Profile"})) 
async def my_profile_handler(
    message: types.Message, 
    state: FSMContext, 
    session: AsyncSession, 
    l10n: FluentLocalization
):
    repo = UserRepo(session)
    user = await repo.get_user(message.from_user.id)
    
    if user and user.steam_id:
        await message.answer(
            l10n.format_value("profile-info", {
                "steamid": user.steam_id,
                "date": user.created_at.strftime('%d.%m.%Y')
            }),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            l10n.format_value("profile-connect-title") + "\n\n" + l10n.format_value("profile-connect-text"),
            reply_markup=get_onboarding_kb(l10n),
            parse_mode="HTML"
        )
        await state.set_state(UserStates.waiting_for_steam_link)

@router.message(UserStates.waiting_for_steam_link)
async def process_steam_link(
    message: types.Message, 
    state: FSMContext, 
    session: AsyncSession, 
    l10n: FluentLocalization
):
    input_text = message.text.strip()
    
    # 1. Пытаемся получить ID
    steam_id = await steam_service.resolve_vanity_url(input_text)
    
    if not steam_id:
        await message.answer(l10n.format_value("err-profile-not-found"))
        return

    # 2. Проверяем доступность игр
    await message.answer(l10n.format_value("status-checking"))
    games = await steam_service.get_owned_games(steam_id)
    
    if games is None:
        await message.answer(l10n.format_value("err-profile-hidden"), parse_mode="HTML")
        return

    # 3. Получаем инфо о юзере
    player_summary = await steam_service.get_player_summary(steam_id)
    username = player_summary.get('personaname', 'Unknown')
    avatar = player_summary.get('avatarfull')

    # 4. Сохраняем в БД
    repo = UserRepo(session)
    await repo.create_or_update(
        telegram_id=message.from_user.id,
        steam_id=int(steam_id),
        username=username,
        avatar=avatar
    )
    
    await repo.update_library(message.from_user.id, games)

    await state.clear()
    await message.answer(
        l10n.format_value("success-connected", {
            "username": username,
            "count": len(games)
        }),
        parse_mode="HTML"
    )