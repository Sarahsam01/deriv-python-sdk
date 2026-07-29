"""
===========================================================
Deriv SDK

Tick Stream Service

Responsibilities
----------------
• Subscribe to live ticks
• Parse tick messages
• Register subscriptions
• Route streamed ticks

Version : 3.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any, Protocol

from deriv_sdk.logger import get_logger
from deriv_sdk.streaming.manager import SubscriptionManager
from deriv_sdk.streaming.models import Tick, TickResponse
from deriv_sdk.streaming.subscription import Subscription


class WebSocketProtocol(Protocol):
    """
    Protocol describing the websocket interface required by
    TickStream.
    """

    async def request(
        self,
        message: dict[str, Any],
        *,
        expected: str,
    ) -> dict[str, Any]: ...


class TickStream:
    """
    Live tick streaming service.
    """

    def __init__(
        self,
        websocket: WebSocketProtocol,
        manager: SubscriptionManager,
    ) -> None:
        self._websocket = websocket
        self._manager = manager

        self._logger = get_logger(__name__)

    async def subscribe(
        self,
        symbol: str,
    ) -> Subscription[Tick]:
        """
        Subscribe to live ticks.

        Parameters
        ----------
        symbol : str
            Market symbol.

        Returns
        -------
        Subscription[Tick]
            Live tick subscription.
        """

        payload = {
            "ticks": symbol,
            "subscribe": 1,
        }

        self._logger.debug(
            "Subscribing to ticks.",
            symbol=symbol,
        )

        response = await self._websocket.request(
            payload,
            expected="tick",
        )

        tick_response = TickResponse.model_validate(response)

        subscription_data = tick_response.subscription

        if subscription_data is None or "id" not in subscription_data:
            raise RuntimeError("Deriv did not return a subscription ID.")

        subscription_id = str(subscription_data["id"])

        subscription = Subscription[Tick](
            subscription_id=subscription_id,
            websocket=self._websocket,
        )

        self._manager.register(subscription)

        await subscription.put(
            tick_response.tick,
        )

        self._logger.info(
            "Tick subscription created.",
            symbol=symbol,
            subscription_id=subscription.id,
        )

        return subscription

    async def dispatch(
        self,
        message: dict[str, Any],
    ) -> bool:
        """
        Dispatch a streamed tick message to its subscription.

        Returns
        -------
        bool
            True if a subscription handled the tick.
        """

        subscription = message.get("subscription")

        if not isinstance(subscription, dict):
            return False

        subscription_id = subscription.get("id")

        if not isinstance(subscription_id, str):
            return False

        tick = TickResponse.model_validate(message).tick

        return await self._manager.dispatch(
            subscription_id,
            tick,
        )
