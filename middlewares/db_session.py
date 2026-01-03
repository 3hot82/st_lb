# Файл: steam_bot/middlewares/db_session.py

from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Открываем сессию для каждого апдейта (сообщения/кнопки)
        async with self.session_pool() as session:
            # Кладем сессию в data, чтобы хендлер мог её забрать
            data["session"] = session
            # Передаем управление хендлеру
            return await handler(event, data)