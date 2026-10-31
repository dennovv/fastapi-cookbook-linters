from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, asc

import models
import schemas
from database import engine, get_db

app = FastAPI(
    title="API Кулинарной Книги",
    description="Production-ready сервис для управления рецептами",
    version="1.0.0"
)


# Автоматическое создание таблиц при старте приложения
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


# 1. GET /recipes — Получить список всех рецептов (с сортировкой)
@app.get("/recipes", response_model=List[schemas.RecipeListOut], status_code=status.HTTP_200_OK)
async def get_recipes(db: AsyncSession = Depends(get_db)):
    """
    Возвращает список всех рецептов, отсортированных по популярности
    (количество просмотров - убывание), затем по времени готовки (возрастание).
    """
    # Пишем сортировку строго по ТЗ
    query = select(models.Recipe).order_by(
        desc(models.Recipe.views),
        asc(models.Recipe.cooking_time)
    )
    result = await db.execute(query)
    return result.scalars().all()


# 2. GET /recipes/{recipe_id} — Получить детальную информацию о рецепте (+1 к просмотру)
@app.get("/recipes/{recipe_id}", response_model=schemas.RecipeDetailOut, status_code=status.HTTP_200_OK)
async def get_recipe_detail(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """
    Возвращает детальную информацию о конкретном рецепте.
    Каждое открытие увеличивает счетчик просмотров на 1.
    """
    result = await db.execute(select(models.Recipe).where(models.Recipe.id == recipe_id))
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Рецепт с id {recipe_id} не найден"
        )

    # Инкрементируем просмотры
    recipe.views += 1
    await db.commit()  # Сохраняем изменения в базе
    await db.refresh(recipe)  # Обновляем объект актуальными данными из БД

    return recipe


# 3. POST /recipes — Создать новый рецепт
@app.post("/recipes", response_model=schemas.RecipeDetailOut, status_code=status.HTTP_201_CREATED)
async def create_recipe(recipe_in: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)):
    """
    Создает новый рецепт в кулинарной книге.
    """
    new_recipe = models.Recipe(**recipe_in.dict())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe
