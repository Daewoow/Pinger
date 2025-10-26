import pytest
import time
from httpx import AsyncClient, ASGITransport
from app.db.pg import get_db as db
from unittest.mock import AsyncMock
from app.main import app
from app.core.jwt import decode_token, create_access_token


@pytest.mark.skip(reason="Надо соединение с бд, не мокается чего-то, надо будет потом поправить")
@pytest.mark.asyncio
async def test_jwt():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        db.execute = AsyncMock(return_value=None)
        db.commit = AsyncMock()
        db.refresh = AsyncMock()

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


def test_jwt_create_and_decode():
    token = create_access_token("user-id-123", expires_in=2)
    assert token
    payload = decode_token(token)
    assert payload['sub'] == 'user-id-123'
    token2 = create_access_token("u2", expires_in=1)
    time.sleep(1.1)
    with pytest.raises(Exception):
        decode_token(token2)
