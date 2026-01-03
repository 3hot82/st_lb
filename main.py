# Файл: steam_bot/main.py

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from config import conf
from database.core import session_maker
from middlewares.db_session import DbSessionMiddleware
from handlers import get_handlers_router

async def main():
    # Настройка логов
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout
    )
    logger = logging.getLogger(__name__)

    # Инициализация
    bot = Bot(token=conf.bot_token)
    dp = Dispatcher()

    # Подключаем Middleware (БД)
    # Теперь в каждый хендлер будет прилетать аргумент session
    dp.update.middleware(DbSessionMiddleware(session_pool=session_maker))

    # Подключаем Хендлеры
    dp.include_router(get_handlers_router())

    logger.info("🚀 Бот запускается...")
    
    # Удаляем вебхуки (чтобы не обрабатывать старые обновления)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запуск
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Бот остановлен вручную.")