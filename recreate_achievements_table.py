import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from database.models.base import Base
from config import conf
from database.models.game import Achievement 

async def recreate_table():
    engine = create_async_engine(conf.database_url, echo=True)
    async with engine.begin() as conn:
        print("🗑 Удаляем старую таблицу achievements...")
        await conn.execute(text("DROP TABLE IF EXISTS achievements CASCADE;"))
        
        print("🆕 Создаем новую таблицу...")
        await conn.run_sync(Base.metadata.create_all)
        
        # === ЯВНОЕ СОЗДАНИЕ ОГРАНИЧЕНИЯ ===
        print("🔒 Добавляем уникальное ограничение...")
        # Если SQLAlchemy не создала его сама, создадим вручную
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'uix_game_achievement') THEN
                    ALTER TABLE achievements ADD CONSTRAINT uix_game_achievement UNIQUE (game_id, api_name);
                END IF;
            END
            $$;
        """))
        
    print("✅ Таблица achievements пересоздана и настроена!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(recreate_table())