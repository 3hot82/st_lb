from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import conf

# Создаем асинхронный движок
# echo=False, чтобы не засорять консоль SQL-запросами (поставь True для отладки)
engine = create_async_engine(conf.database_url, echo=False)

# Фабрика сессий. Через неё мы будем получать доступ к БД в хендлерах.
# expire_on_commit=False важен для асинхронной работы.
session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    """
    Генератор сессий для использования в зависимостях (если понадобится)
    или для ручного вызова.
    """
    async with session_maker() as session:
        yield session