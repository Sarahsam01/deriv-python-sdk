import asyncio
from unittest.mock import AsyncMock

import pytest

from deriv_sdk.exceptions import TimeoutError

# ==========================================================
# API Error Response
# ==========================================================


@pytest.mark.asyncio
async def test_concurrent_requests(websocket):
    websocket._connection = AsyncMock()
    websocket._connected = True

    first = asyncio.create_task(websocket.request({"ping": 1}, expected="ping"))
    second = asyncio.create_task(websocket.request({"time": 1}, expected="time"))

    await asyncio.sleep(0)

    assert set(websocket._pending) == {1, 2}

    websocket._pending[1].set_result({"req_id": 1, "msg_type": "ping"})
    websocket._pending[2].set_result({"req_id": 2, "msg_type": "time"})

    assert await first == {"req_id": 1, "msg_type": "ping"}
    assert await second == {"req_id": 2, "msg_type": "time"}
    assert websocket._pending == {}


@pytest.mark.asyncio
async def test_disconnect_cancels_pending_requests(websocket):
    websocket._connection = AsyncMock()
    websocket._connected = True

    task = asyncio.create_task(websocket.request({"ping": 1}, expected="ping"))

    await asyncio.sleep(0)
    assert websocket._pending

    websocket._cancel_pending()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert websocket._pending == {}


@pytest.mark.asyncio
async def test_late_response_after_timeout_does_not_crash(websocket):
    websocket._connection = AsyncMock()
    websocket._connected = True

    assert not websocket._registry.resolve(
        999,
        {"req_id": 999, "msg_type": "ping"},
    )


@pytest.mark.asyncio
async def test_streaming_message_dispatch(websocket):
    market = AsyncMock()
    market.dispatch_stream = AsyncMock(return_value=True)
    websocket.register_market_service(market)

    handled = await websocket._dispatch_stream(
        {
            "msg_type": "tick",
            "subscription": {"id": "abc"},
        }
    )

    assert handled
    market.dispatch_stream.assert_awaited_once()


@pytest.mark.asyncio
async def test_request_api_error(websocket):
    websocket._connection = AsyncMock()
    websocket._connected = True

    task = asyncio.create_task(
        websocket.request(
            {"ping": 1},
            expected="ping",
        )
    )

    await asyncio.sleep(0)

    req_id = next(iter(websocket._pending))

    websocket._pending[req_id].set_result(
        {
            "req_id": req_id,
            "msg_type": "ping",
            "error": {
                "code": "InvalidToken",
                "message": "Invalid API token.",
            },
        }
    )

    with pytest.raises(RuntimeError):
        await task


# ==========================================================
# Unexpected Message Type
# ==========================================================


@pytest.mark.asyncio
async def test_request_wrong_msg_type(websocket):
    websocket._connection = AsyncMock()
    websocket._connected = True

    task = asyncio.create_task(
        websocket.request(
            {"ping": 1},
            expected="ping",
        )
    )

    await asyncio.sleep(0)

    req_id = next(iter(websocket._pending))

    websocket._pending[req_id].set_result(
        {
            "req_id": req_id,
            "msg_type": "authorize",
        }
    )

    with pytest.raises(RuntimeError):
        await task


# ==========================================================
# Timeout
# ==========================================================


@pytest.mark.asyncio
async def test_request_timeout(websocket):
    websocket._connection = AsyncMock()
    websocket._connected = True

    with pytest.raises(TimeoutError):
        await websocket.request(
            {"ping": 1},
            expected="ping",
            timeout=0.01,
        )


# ==========================================================
# Ping
# ==========================================================


@pytest.mark.asyncio
async def test_ping(websocket):
    websocket._connection = AsyncMock()
    websocket._connected = True

    websocket._connection.ping = AsyncMock()

    await websocket.ping()

    websocket._connection.ping.assert_awaited_once()


# ==========================================================
# Close Alias
# ==========================================================


@pytest.mark.asyncio
async def test_close(websocket):
    called = False

    async def fake_disconnect():
        nonlocal called
        called = True

    websocket.disconnect = fake_disconnect

    await websocket.close()

    assert called


# ==========================================================
# __repr__
# ==========================================================


def test_repr(websocket):
    text = repr(websocket)

    assert isinstance(text, str)
    assert "WebSocketClient" in text
    assert "connected=" in text
    assert "pending=" in text
