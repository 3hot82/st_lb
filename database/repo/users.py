from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from database.models import User, UserLibrary, Game

class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()

    async def create_or_update(self, telegram_id: int, steam_id: int, username: str = None, avatar: str = None):
        user = await self.get_user(telegram_id)
        
        if not user:
            user = User(telegram_id=telegram_id, steam_id=steam_id)
            self.session.add(user)
        else:
            # Если steam_id > 0, обновляем его. Если 0 (заглушка), не трогаем.
            if steam_id > 0:
                user.steam_id = steam_id
        
        if username: user.username = username
        # if avatar: user.avatar_url = avatar
        
        await self.session.commit()
        return user

    async def update_library(self, telegram_id: int, games_data: list):
        """
        Обновляет библиотеку. Сохраняет ТОЛЬКО те игры, которые есть в нашей базе.
        """
        # 1. Удаляем старое
        await self.session.execute(
            delete(UserLibrary).where(UserLibrary.user_id == telegram_id)
        )
        
        # 2. Получаем список ID всех игр, которые есть у нас в базе
        steam_app_ids = [g['appid'] for g in games_data if g.get('playtime_forever', 0) > 0]
        
        if not steam_app_ids:
            return

        # Ищем, какие из этих ID есть в нашей базе
        result = await self.session.execute(
            select(Game.id).where(Game.id.in_(steam_app_ids))
        )
        existing_ids = set(result.scalars().all()) # Множество существующих ID
        
        # 3. Формируем список для вставки
        library_items = []
        for g in games_data:
            app_id = g['appid']
            
            # Если игра есть в нашей базе И в неё играли
            if app_id in existing_ids and g.get('playtime_forever', 0) > 0:
                item = UserLibrary(
                    user_id=telegram_id,
                    game_id=app_id,
                    playtime_forever=g.get('playtime_forever', 0),
                    playtime_2weeks=g.get('playtime_2weeks', 0)
                )
                library_items.append(item)
        
        # 4. Сохраняем
        if library_items:
            self.session.add_all(library_items)
            await self.session.commit()

    async def set_language(self, telegram_id: int, language_code: str):
        """
        Обновляет язык пользователя в базе данных.
        """
        stmt = update(User).where(User.telegram_id == telegram_id).values(language=language_code)
        await self.session.execute(stmt)
        await self.session.commit()