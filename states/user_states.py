# Файл: steam_bot/states/user_states.py

from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    # Состояние, когда бот ждет ссылку на Steam
    waiting_for_steam_link = State()
    
    # Состояние, когда бот ждет поисковый запрос (если мы сделаем отдельную кнопку "Поиск")
    waiting_for_search = State()