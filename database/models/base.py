# Файл: steam_bot/database/models/base.py

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Позволяет не писать __tablename__ каждый раз вручную (опционально),
    но мы будем писать явно для порядка.
    """
    pass