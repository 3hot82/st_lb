import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import conf
from database.models import Game

# ID игры Detroit
TARGET_ID = 1222140 

async def inspect_media():
    engine = create_async_engine(conf.database_url, echo=False)
    # Используем фабрику сессий
    session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_maker() as session:
        print(f"🔎 Проверяем медиа для ID: {TARGET_ID}...\n")

        result = await session.execute(select(Game).where(Game.id == TARGET_ID))
        game = result.scalars().first()

        if not game:
            print("❌ Игра не найдена в базе.")
            return

        extra = game.extra_data or {}
        locales = game.locales or {}
        ru_data = locales.get('ru', {})

        # 1. ОБЛОЖКА
        print(f"🖼 HEADER IMAGE (Обложка):")
        print(f"   {ru_data.get('header_image')}")
        print("-" * 40)

        # 2. СКРИНШОТЫ
        screenshots = extra.get('screenshots', [])
        print(f"📸 SCREENSHOTS (Всего: {len(screenshots)}):")
        for i, url in enumerate(screenshots):
            print(f"   {i+1}. {url}")
        
        print("-" * 40)

        # 3. ВИДЕО (Трейлеры)
        movies = extra.get('movies', [])
        print(f"🎥 MOVIES (Всего: {len(movies)}):")
        if not movies:
            print("   (Список пуст)")
        else:
            for i, url in enumerate(movies):
                print(f"   {i+1}. {url}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(inspect_media())