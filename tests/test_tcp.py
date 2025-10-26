import pytest
import asyncio
from unittest.mock import AsyncMock
from app.services.tcp_pinger import TcpPinger
from app.services.pinger import Pinger


@pytest.mark.asyncio
async def test_tcp_pinger_success(monkeypatch):
    async def fake_open_connection(host, port):
        reader = AsyncMock()
        writer = AsyncMock()
        return reader, writer

    monkeypatch.setattr(asyncio, "open_connection", fake_open_connection)
    monkeypatch.setattr(asyncio, "wait_for", lambda coro, timeout: coro)  # просто возвращаем coroutine

    project = {"host": "example.com", "port": 80, "timeout_s": 1}

    pinger = TcpPinger()

    result = await pinger.check(project)

    assert result is True


@pytest.mark.asyncio
async def test_tcp_pinger_connection_error(monkeypatch):
    async def fake_open_connection(host, port):
        raise ConnectionRefusedError("Connection failed")

    monkeypatch.setattr(asyncio, "open_connection", fake_open_connection)
    monkeypatch.setattr(asyncio, "wait_for", lambda coro, timeout: coro)
    called = {}

    async def fake_alert_error(project, msg):
        called["project"] = project
        called["msg"] = msg

    monkeypatch.setattr(Pinger, "alert_error", fake_alert_error)

    project = {"host": "bad.host", "port": 1234}

    pinger = TcpPinger()
    result = await pinger.check(project)

    assert result is False
    assert called["project"]["host"] == "bad.host"
    assert "Connection failed" in called["msg"]


@pytest.mark.asyncio
async def test_tcp_pinger_timeout(monkeypatch):
    async def fake_open_connection(host, port):
        await asyncio.sleep(999)

    async def fake_wait_for(coro, timeout):
        raise asyncio.TimeoutError("timeout")

    monkeypatch.setattr(asyncio, "open_connection", fake_open_connection)
    monkeypatch.setattr(asyncio, "wait_for", fake_wait_for)

    called = {}

    async def fake_alert_error(project, msg):
        called["msg"] = msg

    monkeypatch.setattr(Pinger, "alert_error", fake_alert_error)

    project = {"host": "timeout.host", "port": 8080, "timeout_s": 1}

    pinger = TcpPinger()
    result = await pinger.check(project)

    assert result is False
    assert "timeout" in called["msg"].lower()
