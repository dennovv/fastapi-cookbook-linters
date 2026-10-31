from pydantic import BaseModel, Field


# Базовая схема с общими полями
class RecipeBase(BaseModel):
    title: str = Field(..., example="Блины классические", min_length=2, max_length=100)
    cooking_time: int = Field(
        ..., example=30, description="Время готовки в минутах", gt=0
    )


# Схема для СОЗДАНИЯ (POST) — тут мы передаем всё, кроме id и просмотров
class RecipeCreate(RecipeBase):
    ingredients: str = Field(..., example="Мука, молоко, яйца, сахар")
    description: str = Field(..., example="Смешать ингредиенты, выпекать на сковороде.")


# Схема для СПИСКА (GET /recipes) — по ТЗ только название, просмотры, время
class RecipeListOut(RecipeBase):
    views: int = Field(..., description="Количество просмотров данного рецепта")

    class Config:
        orm_mode = True  # Для совместимости со SQLAlchemy (Pydantic v1)


# Схема для ДЕТАЛЕЙ (GET /recipes/{id}) — тут все поля, включая ингредиенты и описание
class RecipeDetailOut(RecipeBase):
    id: int
    views: int
    ingredients: str
    description: str

    class Config:
        orm_mode = True
