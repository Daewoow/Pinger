import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_jwt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/auth/register", json={
            "email": "user@example.com",
            "password": "secret123"
        })
        assert res.status_code == 200
        token = res.json()["access_token"]
        assert token

        res = await ac.post("/api/auth/login", json={
            "email": "user@example.com",
            "password": "secret123"
        })
        assert res.status_code == 200
        login_token = res.json()["access_token"]
        assert login_token != ""
