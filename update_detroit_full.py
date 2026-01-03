import asyncio
import aiohttp
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update
from database.models import Game # Убедись, что путь правильный
from config import conf

TARGET_ID = 1222140 # Detroit: Become Human

async def fetch_store_data(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=ru&l=russian"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data[str(app_id)]['success']:
                    return data[str(app_id)]['data']
    return None

async def update_game():
    print(f"🚀 Обновляем данные для Detroit (ID: {TARGET_ID})...")
    
    data = await fetch_store_data(TARGET_ID)
    if not data:
        print("❌ Не удалось получить данные из Steam.")
        return

    # 1. Собираем медиа (Скриншоты + Видео)
    screenshots = [s['path_full'] for s in data.get('screenshots', [])]
    movies = []
    if 'movies' in data:
        for m in data['movies']:
            # Берем mp4 в 480p (чтобы телеграм быстро грузил)
            if 'mp4' in m:
                movies.append(m['mp4'].get('480', m['mp4'].get('max')))
    
    # 2. Собираем описание
    locales = {
        "ru": {
            "short_desc": data.get('short_description'),
            "detailed_desc": data.get('detailed_description'), # HTML описание
            "header_image": data.get('header_image')
        }
    }

    # 3. Технические данные
    extra_data = {
        "screenshots": screenshots,
        "movies": movies,
        "developers": data.get('developers'),
        "publishers": data.get('publishers'),
        "metacritic": data.get('metacritic', {}).get('score'),
        "pc_requirements": data.get('pc_requirements', {})
    }

    # 4. Запись в БД
    engine = create_async_engine(conf.database_url, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with async_session() as session:
        result = await session.execute(select(Game).where(Game.id == TARGET_ID))
        game = result.scalars().first()

        if not game:
            print("Игра не найдена в базе, создаю...")
            game = Game(id=TARGET_ID, name=data['name'])
            session.add(game)
        
        # Обновляем поля
        game.price_current = data.get('price_overview', {}).get('final', 0) / 100
        game.metacritic_score = extra_data['metacritic'] or 0
        game.locales = locales
        game.extra_data = extra_data
        
        await session.commit()
        print("✅ Данные обновлены! Скриншотов:", len(screenshots), "Видео:", len(movies))

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_game())