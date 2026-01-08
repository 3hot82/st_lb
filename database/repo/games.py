import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, or_, and_, func, case
from database.models import Game, Achievement # <--- Добавлен Achievement
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

    # === МЕТОДЫ ДЛЯ АЧИВОК ===
    async def get_achievements(self, game_id: int, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        # Сортировка по редкости (самые частые первыми)
        stmt = select(Achievement).where(Achievement.game_id == game_id)\
            .order_by(Achievement.global_percent.desc())\
            .limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_achievements(self, game_id: int) -> int:
        stmt = select(func.count(Achievement.id)).where(Achievement.game_id == game_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    # === ПОИСК ===
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
            logging.error(f"Search error: {e}")
            return []