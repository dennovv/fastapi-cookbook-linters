import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

import models
from database import engine
from main import app

pytestmark = pytest.mark.asyncio

BASE_URL = "http://testserver"
transport = ASGITransport(app=app)


async def init_test_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


asyncio.run(init_test_db())


async def test_create_recipe() -> None:
    payload = {
        "title": "Тестовый пирог",
        "cooking_time": 45,
        "ingredients": "Мука, сахар, яблоки",
        "description": "Смешать и запекать 45 минут.",
    }

    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.post("/recipes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["views"] == 0
    assert "id" in data


async def test_get_recipe_detail_and_increment_views() -> None:
    payload = {
        "title": "Суп тестовый",
        "cooking_time": 20,
        "ingredients": "Вода, соль",
        "description": "Вскипятить воду, посолить.",
    }

    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        create_resp = await client.post("/recipes", json=payload)
        recipe_id = create_resp.json()["id"]

        detail_resp1 = await client.get(f"/recipes/{recipe_id}")
        assert detail_resp1.status_code == 200
        assert detail_resp1.json()["views"] == 1

        detail_resp2 = await client.get(f"/recipes/{recipe_id}")
        assert detail_resp2.status_code == 200
        assert detail_resp2.json()["views"] == 2
