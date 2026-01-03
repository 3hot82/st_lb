import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from database.models.base import Base
from database.models.user import User, UserLibrary
from config import conf

async def init_db():
    print("🚀 Создаем таблицы пользователей...")
    engine = create_async_engine(conf.database_url, echo=True)
    
    async with engine.begin() as conn:
        # Создаст таблицы users и user_library, если их нет
        await conn.run_sync(Base.metadata.create_all)
        
    print("✅ Таблицы созданы!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())