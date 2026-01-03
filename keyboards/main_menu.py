# Файл: steam_bot/keyboards/main_menu.py

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    
    # Основные кнопки
    builder.row(
        KeyboardButton(text="👤 Мой профиль"),
        KeyboardButton(text="🎮 Поиск игр")
    )
    builder.row(
        KeyboardButton(text="🎲 Случайная игра"), # Можно реализовать позже
        KeyboardButton(text="⚙️ Настройки")
    )
    
    return builder.as_markup(resize_keyboard=True)

def get_onboarding_kb() -> InlineKeyboardMarkup:
    """Кнопка помощи при регистрации"""
    builder = InlineKeyboardBuilder()
    builder.button(text="❓ Где взять ссылку?", callback_data="help_steam_link")
    return builder.as_markup()