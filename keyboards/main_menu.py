from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from fluent.runtime import FluentLocalization

def get_main_menu(l10n: FluentLocalization) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    # Основные кнопки
    builder.row(
        KeyboardButton(text=l10n.format_value("btn-profile")),
        KeyboardButton(text=l10n.format_value("btn-search"))
    )
    builder.row(
        KeyboardButton(text=l10n.format_value("btn-random")),
        KeyboardButton(text=l10n.format_value("btn-settings"))
    )
    
    return builder.as_markup(resize_keyboard=True)

def get_onboarding_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    """Кнопка помощи при регистрации"""
    builder = InlineKeyboardBuilder()
    builder.button(text=l10n.format_value("profile-btn-help"), callback_data="help_steam_link")
    return builder.as_markup()