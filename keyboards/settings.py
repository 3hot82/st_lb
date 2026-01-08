from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from fluent.runtime import FluentLocalization

def get_settings_kb(l10n: FluentLocalization) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Кнопка смены языка
    builder.button(text=l10n.format_value("settings-lang-btn"), callback_data="settings_lang")
    return builder.as_markup()

def get_language_selection_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Кнопки выбора языка (hardcoded, так как названия языков не меняются)
    builder.button(text="🇷🇺 Русский", callback_data="set_lang_ru")
    builder.button(text="🇬🇧 English", callback_data="set_lang_en")
    builder.button(text="⬅️ Back", callback_data="settings_main")
    builder.adjust(1)
    return builder.as_markup()