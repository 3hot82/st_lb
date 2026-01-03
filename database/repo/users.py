from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from database.models import User, UserLibrary, Game

class UserRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, telegram_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalars().first()

    async def create_or_update(self, telegram_id: int, steam_id: int, username: str = None, avatar: str = None, country: str = None):
        """
        Создает или обновляет пользователя.
        country: Код страны (например, 'KZ', 'RU', 'US'). Если None, не обновляем.
        """
        user = await self.get_user(telegram_id)
        
        if not user:
            user = User(telegram_id=telegram_id, steam_id=steam_id)
            self.session.add(user)
        else:
            user.steam_id = steam_id
        
        if username: user.username = username
        if avatar: user.avatar_url = avatar
        
        # Обновляем страну, только если она пришла из Steam
        if country:
            user.country = country
        
        await self.session.commit()
        return user

    async def update_library(self, telegram_id: int, games_data: list):
        """
        Обновляет библиотеку игр пользователя.
        Сохраняет только те игры, которые уже есть в нашей базе данных (таблица games).
        """
        # 1. Удаляем старые записи библиотеки для этого юзера
        await self.session.execute(
            delete(UserLibrary).where(UserLibrary.user_id == telegram_id)
        )
        
        # 2. Собираем ID игр из полученных данных (где время игры > 0)
        steam_app_ids = [g['appid'] for g in games_data if g.get('playtime_forever', 0) > 0]
        
        if not steam_app_ids:
            return

        # 3. Ищем, какие из этих ID реально существуют в нашей таблице games
        # (Чтобы не пытаться добавить связь с несуществующей игрой)
        result = await self.session.execute(
            select(Game.id).where(Game.id.in_(steam_app_ids))
        )
        existing_ids = set(result.scalars().all()) # Множество ID, которые есть в базе
        
        # 4. Формируем список объектов для вставки
        library_items = []
        for g in games_data:
            app_id = g['appid']
            
            if app_id in existing_ids and g.get('playtime_forever', 0) > 0:
                item = UserLibrary(
                    user_id=telegram_id,
                    game_id=app_id,
                    playtime_forever=g.get('playtime_forever', 0),
                    playtime_2weeks=g.get('playtime_2weeks', 0)
                )
                library_items.append(item)
        
        # 5. Массовая вставка
        if library_items:
            self.session.add_all(library_items)
            await self.session.commit()