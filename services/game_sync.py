import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from database.models.game import Achievement
from services.steam import steam_service

async def sync_game_achievements(session: AsyncSession, game_id: int) -> bool:
    """
    Скачивает ачивки из Steam (EN + RU + Статистика) и сохраняет в БД.
    Возвращает True, если ачивки найдены и сохранены.
    """
    logging.info(f"🔄 Syncing achievements for Game ID: {game_id}...")

    # 1. Запрашиваем данные параллельно
    stats_task = steam_service.get_global_achievement_percentages(game_id)
    schema_en_task = steam_service.get_game_schema(game_id, "english")
    schema_ru_task = steam_service.get_game_schema(game_id, "russian")

    # Ждем выполнения
    stats, schema_en, schema_ru = await asyncio.gather(stats_task, schema_en_task, schema_ru_task)

    if not schema_en:
        logging.warning(f"❌ Ачивки для {game_id} не найдены в Steam.")
        return False

    achievements_to_insert = []

    # 2. Объединяем данные
    for api_name, data_en in schema_en.items():
        data_ru = schema_ru.get(api_name, {})
        
        # Безопасное получение процента
        raw_percent = stats.get(api_name, 0.0)
        try:
            percent = float(raw_percent)
        except (ValueError, TypeError):
            percent = 0.0
        
        icon_url = data_en.get('icon')
        
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
            "game_id": game_id,
            "api_name": api_name,
            "icon_url": icon_url,
            "global_percent": percent,
            "is_hidden": is_hidden,
            "locales": locales
        }
        achievements_to_insert.append(ach_data)

    if not achievements_to_insert:
        return False

    # 3. Сохраняем в БД (Mass Upsert)
    try:
        stmt = insert(Achievement).values(achievements_to_insert)
        
        update_stmt = stmt.on_conflict_do_update(
            constraint='uix_game_achievement',
            set_={
                "icon_url": stmt.excluded.icon_url,
                "global_percent": stmt.excluded.global_percent,
                "locales": stmt.excluded.locales,
                "is_hidden": stmt.excluded.is_hidden
            }
        )
        
        await session.execute(update_stmt)
        await session.commit()
        logging.info(f"✅ Загружено {len(achievements_to_insert)} ачивок для {game_id}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Ошибка сохранения ачивок: {e}")
        await session.rollback()
        return False