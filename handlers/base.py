# Файл: steam_bot/handlers/base.py

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.main_menu import get_main_menu
from database.repo.users import UserRepo

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.clear() # Сбрасываем любые старые состояния
    
    user_repo = UserRepo(session)
    user = await user_repo.get_user(message.from_user.id)
    
    if user and user.steam_id:
        # Если юзер уже есть в базе
        await message.answer(
            f"👋 С возвращением, <b>{user.username or message.from_user.first_name}</b>!\n"
            "Ты можешь искать игры или посмотреть свой профиль.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )
    else:
        # Если новенький
        await message.answer(
            "👋 <b>Привет! Я Steam Explorer.</b>\n\n"
            "Я помогу тебе:\n"
            "🔹 Следить за ачивками\n"
            "🔹 Искать игры (даже если ты забыл название)\n"
            "🔹 Узнать время прохождения\n\n"
            "Чтобы начать, нажми кнопку <b>'👤 Мой профиль'</b> или просто напиши название игры.",
            reply_markup=get_main_menu(),
            parse_mode="HTML"
        )