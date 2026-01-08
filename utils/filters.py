# utils/filters.py
from aiogram.filters import Filter
from aiogram.types import Message
from utils.i18n import get_l10n

class LocalizedTextFilter(Filter):
    def __init__(self, key: str):
        self.key = key

    async def __call__(self, message: Message, l10n) -> bool:
        # Сравниваем текст сообщения с переводом этого ключа
        return message.text == l10n.format(self.key)