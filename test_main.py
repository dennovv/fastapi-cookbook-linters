import pytest
from httpx import ASGITransport, AsyncClient  # Добавили импорт ASGITransport

from main import app

pytestmark = pytest.mark.asyncio

BASE_URL = "http://testserver"
# Создаем транспорт для нашего FastAPI приложения
transport = ASGITransport(app=app)


async def test_create_recipe():
    """Тест успешного создания нового рецепта через POST."""
    payload = {
        "title": "Тестовый пирог",
        "cooking_time": 45,
        "ingredients": "Мука, сахар, яблоки",
        "description": "Смешать и запекать 45 минут.",
    }

    # Вместо app=app передаем transport=transport
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.post("/recipes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["views"] == 0
    assert "id" in data


async def test_get_recipe_detail_and_increment_views():
    """Тест получения деталей рецепта и проверки увеличения счетчика просмотров."""
    payload = {
        "title": "Суп тестовый",
        "cooking_time": 20,
        "ingredients": "Вода, соль",
        "description": "Вскипятить воду, посолить.",
    }

    # И здесь тоже меняем на transport=transport
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        # Создаем
        create_resp = await client.post("/recipes", json=payload)
        recipe_id = create_resp.json()["id"]

        # Запрашиваем детали ОДИН раз
        detail_resp1 = await client.get(f"/recipes/{recipe_id}")
        assert detail_resp1.status_code == 200
        assert detail_resp1.json()["views"] == 1

        # Запрашиваем детали ВТОРОЙ раз
        detail_resp2 = await client.get(f"/recipes/{recipe_id}")
        assert detail_resp2.status_code == 200
        assert detail_resp2.json()["views"] == 2
