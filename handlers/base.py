from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from fluent.runtime import FluentLocalization

from keyboards.main_menu import get_main_menu
from database.repo.users import UserRepo

router = Router()

@router.message(CommandStart())
async def cmd_start(
    message: types.Message, 
    state: FSMContext, 
    session: AsyncSession, 
    l10n: FluentLocalization
):
    await state.clear()
    
    user_repo = UserRepo(session)
    user = await user_repo.get_user(message.from_user.id)
    
    if user and user.steam_id:
        # Если юзер уже есть в базе
        await message.answer(
            l10n.format_value("start-welcome-back", {"name": user.username or message.from_user.first_name}),
            reply_markup=get_main_menu(l10n),
            parse_mode="HTML"
        )
    else:
        # Если новенький
        await message.answer(
            l10n.format_value("start-welcome-new"),
            reply_markup=get_main_menu(l10n),
            parse_mode="HTML"
        )