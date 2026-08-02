from unittest.mock import AsyncMock

import pytest

from deriv_sdk.client import DerivClient
from deriv_sdk.config import SDKConfig


def test_client_construction_and_service_sharing():
    client = DerivClient(app_id="1089")

    assert client.config.app_id == "1089"
    assert client.auth.engine is client.request_engine
    assert client.market.engine is client.request_engine
    assert client.proposal is client.proposal
    assert "DerivClient" in repr(client)


@pytest.mark.asyncio
async def test_client_start_success_with_authorization(monkeypatch):
    client = DerivClient(app_id="1089", api_token="token")
    connect = AsyncMock()
    close = AsyncMock()
    authorize = AsyncMock()
    monkeypatch.setattr(client.transport, "connect", connect)
    monkeypatch.setattr(client.transport, "close", close)
    monkeypatch.setattr(client.auth, "authorize", authorize)

    await client.start()

    connect.assert_awaited_once()
    authorize.assert_awaited_once_with("token")
    close.assert_not_awaited()
    assert client.started


@pytest.mark.asyncio
async def test_client_start_skips_authorization_without_token(monkeypatch):
    client = DerivClient(app_id="1089")
    connect = AsyncMock()
    authorize = AsyncMock()
    monkeypatch.setattr(client.transport, "connect", connect)
    monkeypatch.setattr(client.auth, "authorize", authorize)

    await client.start()

    connect.assert_awaited_once()
    authorize.assert_not_awaited()
    assert client.started


@pytest.mark.asyncio
async def test_client_start_cleanup_on_authorization_failure(monkeypatch):
    client = DerivClient(app_id="1089", api_token="token")
    monkeypatch.setattr(client.transport, "connect", AsyncMock())
    close = AsyncMock()
    monkeypatch.setattr(client.transport, "close", close)
    monkeypatch.setattr(
        client.auth,
        "authorize",
        AsyncMock(side_effect=RuntimeError("denied")),
    )

    with pytest.raises(RuntimeError, match="denied"):
        await client.start()

    close.assert_awaited_once()
    assert not client.started


@pytest.mark.asyncio
async def test_client_start_and_close_are_idempotent(monkeypatch):
    client = DerivClient(app_id="1089")
    connect = AsyncMock()
    close = AsyncMock()
    monkeypatch.setattr(client.transport, "connect", connect)
    monkeypatch.setattr(client.transport, "close", close)

    await client.start()
    await client.start()
    await client.close()
    await client.close()

    connect.assert_awaited_once()
    close.assert_awaited_once()
    assert not client.started


@pytest.mark.asyncio
async def test_client_async_context_manager(monkeypatch):
    client = DerivClient(app_id="1089")
    start = AsyncMock()
    close = AsyncMock()
    monkeypatch.setattr(client, "start", start)
    monkeypatch.setattr(client, "close", close)

    async with client as entered:
        assert entered is client

    start.assert_awaited_once()
    close.assert_awaited_once()


def test_client_uses_supplied_config_without_network():
    config = SDKConfig(app_id="1234", api_token="token")
    client = DerivClient(app_id="ignored", config=config)

    assert client.config is config
