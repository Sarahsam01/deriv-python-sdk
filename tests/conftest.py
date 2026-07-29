from unittest.mock import AsyncMock

import pytest

from deriv_sdk.config import SDKConfig
from deriv_sdk.transport.router import MessageRouter
from deriv_sdk.transport.websocket import WebSocketClient


@pytest.fixture
def config():
    """SDK configuration fixture."""
    return SDKConfig()


@pytest.fixture
def router():
    """Message router fixture."""
    return MessageRouter()


@pytest.fixture
def websocket(config, router):
    """Fresh WebSocketClient for each test."""
    return WebSocketClient(
        config=config,
        router=router,
    )


@pytest.fixture
def mock_connection():
    """Mock websocket connection."""
    connection = AsyncMock()
    connection.send = AsyncMock()
    connection.recv = AsyncMock()
    connection.close = AsyncMock()
    connection.ping = AsyncMock()
    return connection