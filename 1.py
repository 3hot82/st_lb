import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import conf

async def fix_db():
    engine = create_async_engine(conf.database_url, echo=True)
    
    print("🔧 Исправляем таблицу users...")
    
    async with engine.begin() as conn:
        # Добавляем недостающую колонку avatar_url
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR;"))
        
    print("✅ Колонка avatar_url успешно добавлена!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_db())