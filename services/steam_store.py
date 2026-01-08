import asyncio
import aiohttp
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Game

# API Магазина Steam
SEARCH_URL = "https://store.steampowered.com/api/storesearch/"
DETAILS_URL = "https://store.steampowered.com/api/appdetails"

# !!! ВАЖНО: Куки для обхода проверки возраста (18+) !!!
STEAM_COOKIES = {
    "birthtime": "0",
    "lastagecheckage": "1-0-1900",
    "wants_mature_content": "1"
}

async def get_app_details_raw(client: aiohttp.ClientSession, app_id: int, filters: str = None):
    """Базовая функция запроса деталей с куками."""
    params = {"appids": app_id}
    if filters:
        params["filters"] = filters
        
    try:
        # Передаем cookies, чтобы видеть игры 18+
        async with client.get(DETAILS_URL, params=params, cookies=STEAM_COOKIES) as resp:
            if resp.status != 200: return None
            data = await resp.json()
            
            if str(app_id) in data and data[str(app_id)]['success']:
                return data[str(app_id)]['data']
    except Exception:
        pass
    return None

async def search_game_in_steam(query: str) -> int | None:
    """
    Ищет игру в Steam.
    Используем регион US и English для лучшего поиска, но куки позволяют видеть 18+.
    """
    params = {
        "term": query,
        "l": "english", # Ищем на английском (лучше работает поиск)
        "cc": "US"      # Ищем в США (чтобы избежать региональных блоков)
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Получаем список
            async with session.get(SEARCH_URL, params=params, cookies=STEAM_COOKIES) as resp:
                if resp.status != 200: return None
                data = await resp.json()
                
                items = data.get("items", [])
                if not items: return None

            # 2. Проверяем топ-5 результатов
            for item in items[:5]:
                app_id = int(item["id"])
                name = item["name"]
                
                # Запрашиваем тип (game/dlc)
                # Используем basic фильтр для скорости
                details = await get_app_details_raw(session, app_id, filters="basic")
                
                if details:
                    app_type = details.get("type")
                    logging.info(f"🔍 Check: {name} (ID: {app_id}) -> Type: {app_type}")
                    
                    if app_type == "game":
                        return app_id
                else:
                    # Если details вернул None, но название очень похоже, 
                    # возможно API глючит, но это скорее всего та самая игра.
                    # Для Helldivers 2 это спасет ситуацию, если API капризничает.
                    if query.lower() in name.lower():
                        logging.info(f"⚠️ API details failed, but name match: {name}. Assuming it's the game.")
                        return app_id

        except Exception as e:
            logging.error(f"Steam Search Error: {e}")
            
    return None

async def fetch_data_for_locale(client: aiohttp.ClientSession, app_id: int, language: str, region: str):
    """Получает данные с учетом языка и региона."""
    params = {"appids": app_id, "l": language, "cc": region}
    try:
        # Cookies важны и здесь!
        async with client.get(DETAILS_URL, params=params, cookies=STEAM_COOKIES) as resp:
            if resp.status != 200: return None
            raw = await resp.json()
            
            if str(app_id) not in raw or not raw[str(app_id)]['success']:
                return None
            
            return raw[str(app_id)]['data']
    except Exception as e:
        logging.error(f"Error fetching locale {language}: {e}")
        return None

async def fetch_and_save_game(session: AsyncSession, app_id: int) -> Game | None:
    """
    Скачивает данные (RU + EN), сохраняет в БД и возвращает объект Game.
    """
    # 1. Проверка БД
    result = await session.execute(select(Game).where(Game.id == app_id))
    existing_game = result.scalars().first()
    if existing_game:
        return existing_game

    # 2. Скачивание (RU + EN)
    async with aiohttp.ClientSession() as client:
        # RU запрос (cc=RU, чтобы видеть цену в рублях, если доступна)
        task_ru = fetch_data_for_locale(client, app_id, "russian", "ru")
        # EN запрос (cc=US, чтобы видеть всё остальное)
        task_en = fetch_data_for_locale(client, app_id, "english", "us")
        
        data_ru, data_en = await asyncio.gather(task_ru, task_en)

    if not data_ru and not data_en:
        logging.error(f"❌ Failed to fetch data for {app_id} (Age gate or region block?)")
        return None

    # Приоритет данных: EN (технические данные полнее), RU (для описания)
    main_data = data_en if data_en else data_ru
    
    # 3. Сборка данных
    locales = {}
    if data_ru:
        locales["ru"] = {
            "short_desc": data_ru.get('short_description'),
            "header_image": data_ru.get('header_image')
        }
    if data_en:
        locales["en"] = {
            "short_desc": data_en.get('short_description'),
            "header_image": data_en.get('header_image')
        }

    screenshots = [s['path_full'] for s in main_data.get('screenshots', [])]
    movies = []
    if 'movies' in main_data:
        for m in main_data['movies']:
            if 'mp4' in m:
                movies.append(m['mp4'].get('480', m['mp4'].get('max')))

    extra_data = {
        "screenshots": screenshots,
        "movies": movies,
        "developers": main_data.get('developers', []),
        "publishers": main_data.get('publishers', []),
        "pc_requirements": main_data.get('pc_requirements', {})
    }

    # Цена
    price = 0.0
    currency = "USD"
    
    # Пытаемся взять USD
    if data_en and data_en.get('price_overview'):
        price = data_en['price_overview']['final'] / 100
        currency = "USD"
    # Иначе RUB
    elif data_ru and data_ru.get('price_overview'):
        price = data_ru['price_overview']['final'] / 100
        currency = "RUB"

    # 4. Создание объекта
    new_game = Game(
        id=app_id,
        name=main_data['name'],
        price_current=price,
        currency=currency,
        is_free=main_data.get('is_free', False),
        reviews_total=main_data.get('recommendations', {}).get('total', 0),
        achievements_count=main_data.get('achievements', {}).get('total', 0),
        release_date=main_data.get('release_date', {}).get('date'),
        metacritic_score=main_data.get('metacritic', {}).get('score', 0),
        locales=locales,
        extra_data=extra_data
    )

    session.add(new_game)
    try:
        await session.commit()
    except Exception as e:
        logging.error(f"DB Save Error: {e}")
        await session.rollback()
        return None
    
    return new_game