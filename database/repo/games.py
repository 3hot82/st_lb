import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, or_, and_, func, case
from sqlalchemy.orm.attributes import flag_modified # <--- ВАЖНЫЙ ИМПОРТ
from database.models import Game, Achievement
from services.text_utils import clean_query, fix_layout

class GameRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, game_id: int) -> Game | None:
        result = await self.session.execute(select(Game).where(Game.id == game_id))
        return result.scalars().first()
        
    async def get_random_game(self) -> Game | None:
        stmt = select(Game).where(Game.reviews_total > 500).order_by(func.random()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_achievements(self, game_id: int) -> list[Achievement]:
        stmt = select(Achievement).where(Achievement.game_id == game_id).order_by(Achievement.global_percent.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # === ИСПРАВЛЕННЫЙ МЕТОД ===
    async def delete_broken_media(self, game_id: int, broken_url: str):
        """Удаляет URL из списка и ПРИНУДИТЕЛЬНО сохраняет изменения"""
        game = await self.get_by_id(game_id)
        if not game: return False

        # Получаем данные (копируем словарь)
        extra = dict(game.extra_data) if game.extra_data else {}
        changed = False

        # Проверяем скриншоты
        if 'screenshots' in extra and broken_url in extra['screenshots']:
            extra['screenshots'].remove(broken_url)
            changed = True
            logging.warning(f"🗑 Удален битый скриншот: {broken_url}")

        # Проверяем видео
        if 'movies' in extra and broken_url in extra['movies']:
            extra['movies'].remove(broken_url)
            changed = True
            logging.warning(f"🗑 Удалено битое видео: {broken_url}")

        if changed:
            # 1. Обновляем поле
            game.extra_data = extra
            
            # 2. ВАЖНО: Явно помечаем поле как измененное для SQLAlchemy
            flag_modified(game, "extra_data")
            
            # 3. Сохраняем
            await self.session.commit()
            return True
            
        return False

    async def search(self, query: str, limit: int = 10):
        raw_q = query.strip()
        clean_q = clean_query(raw_q)     
        switched_q = fix_layout(raw_q)   
        clean_switched = clean_query(switched_q)
        words = clean_q.split()
        db_clean_name = func.regexp_replace(Game.name, r'[^a-zA-Z0-9а-яА-Я0-9]', ' ', 'g')

        conditions = []
        conditions.append(text("name % :q"))
        conditions.append(text("name % :switched"))
        conditions.append(db_clean_name.ilike(f"%{clean_q}%"))
        conditions.append(db_clean_name.ilike(f"%{clean_switched}%"))
        
        if len(words) > 1:
            word_conditions = [Game.name.ilike(f"%{w}%") for w in words]
            conditions.append(and_(*word_conditions))

        stmt = select(Game).where(or_(*conditions)).order_by(
            case((func.lower(db_clean_name) == func.lower(clean_q), 0), else_=1),
            case((Game.name.ilike(f"{clean_q}%"), 0), else_=1),
            func.length(Game.name).asc(),
            func.similarity(Game.name, clean_q).desc(),
            Game.reviews_total.desc()
        ).limit(limit)

        try:
            result = await self.session.execute(stmt, {"q": clean_q, "switched": clean_switched})
            return result.scalars().all()
        except Exception as e:
            logging.error(f"❌ Ошибка поиска: {e}")
            return []