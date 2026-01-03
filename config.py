import os
from dotenv import load_dotenv
from dataclasses import dataclass

# Загружаем переменные из .env
load_dotenv()

@dataclass
class Config:
    bot_token: str
    steam_api_key: str
    database_url: str

def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN"),
        steam_api_key=os.getenv("STEAM_API_KEY"),
        database_url=os.getenv("DATABASE_URL")
    )

# Создаем экземпляр конфига, чтобы импортировать его везде
conf = load_config()