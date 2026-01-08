from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from utils.i18n import get_l10n
from database.repo.users import UserRepo # Импортируем репозиторий

class I18nMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user: User = data.get("event_from_user")
        session = data.get("session") # Получаем сессию из DbSessionMiddleware
        
        locale = "ru" # Дефолтный язык

        if user and session:
            # 1. Пробуем найти пользователя в БД
            repo = UserRepo(session)
            db_user = await repo.get_user(user.id)
            
            if db_user and db_user.language:
                # Если в БД есть язык, берем его
                locale = db_user.language
            elif user.language_code:
                # Если нет, берем из Телеграма (ru, en, uk -> ru)
                if "ru" in user.language_code or "uk" in user.language_code:
                    locale = "ru"
                else:
                    locale = "en"

        # 2. Создаем объект локализации
        l10n = get_l10n(locale)
        
        # 3. Кладем в data
        data["l10n"] = l10n
        
        return await handler(event, data)