import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.icmp_pinger import IcmpPinger


@pytest.mark.asyncio
async def test_check_success(monkeypatch):

    pinger = IcmpPinger()
    project = {"host": "example.com", "timeout_s": 2}

    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b"pong", b""))

    async def mock_create_subprocess_exec(*args, **kwargs):
        return mock_proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_create_subprocess_exec)
    pinger.alert_error = AsyncMock()

    result = await pinger.check(project)

    assert result is True
    pinger.alert_error.assert_not_called()


@pytest.mark.asyncio
async def test_check_ping_failure(monkeypatch):
    pinger = IcmpPinger()
    project = {"host": "example.com", "timeout_s": 2}

    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.communicate = AsyncMock(return_value=(b"some output", b"error msg"))

    async def mock_create_subprocess_exec(*args, **kwargs):
        return mock_proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_create_subprocess_exec)
    pinger.alert_error = AsyncMock()

    result = await pinger.check(project)

    assert result is False
    pinger.alert_error.assert_called_once()
    args, _ = pinger.alert_error.call_args
    assert "rc=1" in args[1]


@pytest.mark.asyncio
async def test_check_exception(monkeypatch):
    pinger = IcmpPinger()
    project = {"host": "invalid-host", "timeout_s": 2}

    async def mock_create_subprocess_exec(*args, **kwargs):
        raise OSError("command not found")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", mock_create_subprocess_exec)
    pinger.alert_error = AsyncMock()

    result = await pinger.check(project)

    assert result is False
    pinger.alert_error.assert_called_once()
    args, _ = pinger.alert_error.call_args
    assert "command not found" in args[1]
