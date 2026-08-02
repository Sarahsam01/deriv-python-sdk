from __future__ import annotations

import asyncio

import pytest

from deriv_sdk.client import DerivClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_live_client_connects_and_closes(app_id: str) -> None:
    client = DerivClient(app_id=app_id)
    try:
        async with asyncio.timeout(15):
            await client.start()

        assert client.connected
    finally:
        await client.close()

    assert not client.connected


@pytest.mark.asyncio
async def test_live_authorization_when_token_present(
    app_id: str,
    api_token: str | None,
) -> None:
    if api_token is None:
        pytest.skip("DERIV_API_TOKEN is not configured")

    client = DerivClient(app_id=app_id, api_token=api_token)
    try:
        async with asyncio.timeout(15):
            await client.start()

        assert client.authorized
        response = client.auth.authorize_response
        assert response is not None
        assert response.get("authorize") is not None
    finally:
        await client.close()

    assert not client.connected
