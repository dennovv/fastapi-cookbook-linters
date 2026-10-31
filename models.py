from sqlalchemy import Column, Integer, String, Text
from database import Base

class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True, nullable=False)
    cooking_time = Column(Integer, nullable=False)  # Время в минутах
    views = Column(Integer, default=0, nullable=False)  # Количество просмотров
    ingredients = Column(Text, nullable=False)  # Ингредиенты через запятую
    description = Column(Text, nullable=False)  # Текстовое описание
