from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from fluent.runtime import FluentLocalization

from database.repo.users import UserRepo
from keyboards.settings import get_settings_kb, get_language_selection_kb
from keyboards.main_menu import get_main_menu
from utils.i18n import get_l10n # Импортируем функцию получения локализации

router = Router()

# 1. Обработка кнопки "⚙️ Настройки" из главного меню
@router.message(F.text.in_({"⚙️ Настройки", "⚙️ Settings"}))
async def settings_menu(message: types.Message, l10n: FluentLocalization):
    await message.answer(
        l10n.format_value("settings-title"),
        reply_markup=get_settings_kb(l10n),
        parse_mode="HTML"
    )

# 2. Кнопка "Назад" внутри настроек
@router.callback_query(F.data == "settings_main")
async def settings_main_callback(callback: types.CallbackQuery, l10n: FluentLocalization):
    await callback.message.edit_text(
        l10n.format_value("settings-title"),
        reply_markup=get_settings_kb(l10n),
        parse_mode="HTML"
    )

# 3. Меню выбора языка
@router.callback_query(F.data == "settings_lang")
async def settings_lang_menu(callback: types.CallbackQuery, l10n: FluentLocalization):
    await callback.message.edit_text(
        l10n.format_value("settings-select-lang"),
        reply_markup=get_language_selection_kb()
    )

# 4. Сохранение языка (set_lang_ru / set_lang_en)
@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: types.CallbackQuery, session: AsyncSession):
    # Получаем код языка из callback_data (ru или en)
    lang_code = callback.data.split("_")[2] 
    
    # Сохраняем в БД
    repo = UserRepo(session)
    
    # Проверяем, есть ли юзер, если нет - создаем
    user = await repo.get_user(callback.from_user.id)
    if not user:
        await repo.create_or_update(callback.from_user.id, 0)
    
    # Обновляем язык
    await repo.set_language(callback.from_user.id, lang_code)
    
    # Получаем новый переводчик ПРЯМО СЕЙЧАС, чтобы ответить на новом языке
    new_l10n = get_l10n(lang_code)
    
    # Удаляем старое сообщение настроек
    await callback.message.delete()
    
    # Отправляем подтверждение и НОВУЮ клавиатуру меню
    await callback.message.answer(
        new_l10n.format_value("settings-lang-changed"),
        reply_markup=get_main_menu(new_l10n),
        parse_mode="HTML"
    )