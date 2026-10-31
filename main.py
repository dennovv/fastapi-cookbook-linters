from typing import Any, List, Sequence

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

import models
import schemas
from database import engine, get_db

app = FastAPI(
    title="API Кулинарной Книги",
    description="Production-ready сервис для управления рецептами",
    version="1.0.0",
)


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


@app.get(
    "/recipes",
    response_model=List[schemas.RecipeListOut],
    status_code=status.HTTP_200_OK,
)
async def get_recipes(
    db: AsyncSession = Depends(get_db),
) -> Sequence[Any]:
    query = select(models.Recipe).order_by(
        desc(models.Recipe.views), asc(models.Recipe.cooking_time)
    )
    result = await db.execute(query)
    return result.scalars().all()


@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeDetailOut,
    status_code=status.HTTP_200_OK,
)
async def get_recipe_detail(recipe_id: int, db: AsyncSession = Depends(get_db)) -> Any:
    result = await db.execute(
        select(models.Recipe).where(models.Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()

    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Рецепт с id {recipe_id} не найден",
        )

    # Используем setattr, чтобы mypy не ругался на несовместимость Column и int
    current_views = int(recipe.views)
    setattr(recipe, "views", current_views + 1)

    await db.commit()
    await db.refresh(recipe)

    return recipe


@app.post(
    "/recipes",
    response_model=schemas.RecipeDetailOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_recipe(
    recipe_in: schemas.RecipeCreate, db: AsyncSession = Depends(get_db)
) -> Any:
    new_recipe = models.Recipe(**recipe_in.dict())
    db.add(new_recipe)
    await db.commit()
    await db.refresh(new_recipe)
    return new_recipe
