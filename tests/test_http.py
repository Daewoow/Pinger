import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.http_pinger import HttpPinger


import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.http_pinger import HttpPinger


@pytest.mark.asyncio
async def test_http_pinger_success(monkeypatch):
    pinger = HttpPinger()
    project = {"url": "https://example.com", "timeout_s": 5}

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.elapsed.total_seconds.return_value = 0.123

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    mock_async_client_cm = MagicMock()
    mock_async_client_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_async_client_cm.__aexit__ = AsyncMock(return_value=None)

    monkeypatch.setattr("httpx.AsyncClient", lambda *args, **kwargs: mock_async_client_cm)

    pinger.alert_error = AsyncMock()

    result = await pinger.check(project)

    assert result is True
    pinger.alert_error.assert_not_called()


@pytest.mark.asyncio
async def test_http_pinger_error_on_server(monkeypatch):
    pinger = HttpPinger()
    bad = {"url": "https://example.com", "timeout_s": 5}

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.elapsed.total_seconds.return_value = 0.123

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    async def mock_async_client(*args, **kwargs):
        return mock_client

    monkeypatch.setattr("httpx.AsyncClient", mock_async_client)
    pinger.alert_error = AsyncMock()

    result = await pinger.check(bad)

    assert result is False
    pinger.alert_error.assert_called_once()


@pytest.mark.asyncio
async def test_http_pinger_404(monkeypatch):
    pinger = HttpPinger()
    project = {"url": "https://example.com/missing"}

    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.elapsed.total_seconds.return_value = 0.1

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    async def mock_async_client(*args, **kwargs):
        return mock_client

    monkeypatch.setattr("httpx.AsyncClient", mock_async_client)
    pinger.alert_error = AsyncMock()

    result = await pinger.check(project)

    assert result is False
    pinger.alert_error.assert_called_once()


@pytest.mark.asyncio
async def test_http_pinger_exception(monkeypatch):
    pinger = HttpPinger()
    project = {"url": "https://bad.example.com"}

    async def mock_get(*args, **kwargs):
        raise Exception("connection failed")

    mock_client = MagicMock()
    mock_client.get = mock_get

    async def mock_async_client(*args, **kwargs):
        return mock_client

    monkeypatch.setattr("httpx.AsyncClient", mock_async_client)
    pinger.alert_error = AsyncMock()

    result = await pinger.check(project)

    assert result is False
    pinger.alert_error.assert_called_once()
