import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost/steam_bot_db"

async def fix_db():
    engine = create_async_engine(DATABASE_URL, echo=True)
    print("🔄 Обновляем структуру таблицы games...")
    
    async with engine.begin() as conn:
        # Добавляем все колонки, которых может не хватать
        await conn.execute(text("ALTER TABLE games ADD COLUMN IF NOT EXISTS time_plus FLOAT DEFAULT 0;"))
        await conn.execute(text("ALTER TABLE games ADD COLUMN IF NOT EXISTS time_main FLOAT DEFAULT 0;"))
        await conn.execute(text("ALTER TABLE games ADD COLUMN IF NOT EXISTS time_100 FLOAT DEFAULT 0;"))
        await conn.execute(text("ALTER TABLE games ADD COLUMN IF NOT EXISTS hltb_id VARCHAR;"))
        
    print("✅ База данных обновлена!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_db())