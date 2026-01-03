import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import insert
from config import conf
from services.steam import steam_service
from database.models.game import Achievement, Game

# ID игры (Detroit)
TARGET_APP_ID = 1222140 

async def update_achievements():
    print(f"🚀 Начинаем загрузку ачивок для игры ID: {TARGET_APP_ID}...")

    # 1. Запрашиваем данные параллельно
    print("📥 Скачиваем данные из Steam API...")
    stats_task = steam_service.get_global_achievement_percentages(TARGET_APP_ID)
    schema_en_task = steam_service.get_game_schema(TARGET_APP_ID, "english")
    schema_ru_task = steam_service.get_game_schema(TARGET_APP_ID, "russian")

    stats, schema_en, schema_ru = await asyncio.gather(stats_task, schema_en_task, schema_ru_task)

    if not schema_en:
        print("❌ Не удалось получить схему ачивок.")
        return

    print(f"✅ Получено ачивок: {len(schema_en)}")
    
    achievements_to_insert = []

    # 2. Объединяем данные
    for api_name, data_en in schema_en.items():
        data_ru = schema_ru.get(api_name, {})
        
        # === ИСПРАВЛЕНИЕ ОШИБКИ ===
        # Явно преобразуем процент в float, так как API может вернуть строку '6.9'
        raw_percent = stats.get(api_name, 0.0)
        try:
            percent = float(raw_percent)
        except (ValueError, TypeError):
            percent = 0.0
        
        # Иконка (берем из EN)
        icon_url = data_en.get('icon')
        
        # Локализация
        locales = {
            "en": {
                "name": data_en.get('displayName'),
                "desc": data_en.get('description')
            },
            "ru": {
                "name": data_ru.get('displayName', data_en.get('displayName')),
                "desc": data_ru.get('description')
            }
        }

        is_hidden = data_en.get('hidden', 0) == 1

        ach_data = {
            "game_id": TARGET_APP_ID,
            "api_name": api_name,
            "icon_url": icon_url,
            "global_percent": percent, # Теперь это точно число
            "is_hidden": is_hidden,
            "locales": locales
        }
        achievements_to_insert.append(ach_data)

    # 3. Сохраняем в БД
    engine = create_async_engine(conf.database_url, echo=False)
    
    async with engine.begin() as conn:
        # Гарантируем, что игра существует
        await conn.execute(
            insert(Game).values(id=TARGET_APP_ID, name="Detroit: Become Human")
            .on_conflict_do_nothing()
        )

        print(f"💾 Сохраняем {len(achievements_to_insert)} записей в БД...")
        
        stmt = insert(Achievement).values(achievements_to_insert)
        
        # UPSERT
        update_stmt = stmt.on_conflict_do_update(
            constraint='uix_game_achievement',
            set_={
                "icon_url": stmt.excluded.icon_url,
                "global_percent": stmt.excluded.global_percent,
                "locales": stmt.excluded.locales,
                "is_hidden": stmt.excluded.is_hidden
            }
        )
        
        await conn.execute(update_stmt)
    
    print("🎉 Готово! Ачивки загружены.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(update_achievements())