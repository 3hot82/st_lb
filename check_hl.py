import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Твои настройки
DATABASE_URL = "postgresql+asyncpg://postgres:root@localhost/steam_bot_db"

async def check_game():
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    print("🕵️‍♂️ Проверяем базу данных...")

    async with engine.begin() as conn:
        # 1. Проверка конкретно ID 70
        print("\n--- ПОИСК ПО ID 1222140 ---")
        result = await conn.execute(text("SELECT id, name, reviews_total FROM games WHERE id = 1222140"))
        game = result.first()
        
        if game:
            print(f"✅ ИГРА НАЙДЕНА ПО ID!")
            print(f"🆔 ID: {game.id}")
            print(f"📛 Имя в базе: '{game.name}'") # Важно: кавычки покажут, есть ли пробелы
            print(f"👥 Отзывов: {game.reviews_total}")
        else:
            print("❌ Игры с ID 1222140 НЕТ в базе.")

        # 2. Проверка по названию (вдруг ID другой или имя кривое)
        print("\n--- ПОИСК ПО НАЗВАНИЮ '%Half%Life%' ---")
        result = await conn.execute(text("SELECT id, name, reviews_total FROM games WHERE name ILIKE '%Half%Life%' ORDER BY reviews_total DESC LIMIT 10"))
        rows = result.all()
        
        if rows:
            for row in rows:
                print(f"🎮 {row.name} (ID: {row.id}) - Отзывов: {row.reviews_total}")
        else:
            print("❌ Ничего похожего на Half-Life не найдено.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_game())