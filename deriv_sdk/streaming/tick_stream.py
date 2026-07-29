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

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.logger import get_logger
from deriv_sdk.streaming.manager import SubscriptionManager
from deriv_sdk.streaming.models import Tick, TickResponse
from deriv_sdk.streaming.subscription import Subscription


class TickStream:
    """
    Live tick streaming service.
    """

    def __init__(
        self,
        websocket,
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
        """

        payload = {
            "ticks": symbol,
            "subscribe": 1,
        }

        self._logger.debug(
            "Subscribing to ticks.",
            symbol=symbol,
        )

        response: dict[str, Any] = await self._websocket.request(
            payload,
            expected="tick",
        )

        tick_response = TickResponse.model_validate(
            response,
        )

        subscription_data = tick_response.subscription

        if subscription_data is None or "id" not in subscription_data:
            raise RuntimeError("Deriv did not return a subscription ID.")

        subscription = Subscription[Tick](
            subscription_id=subscription_data["id"],
            websocket=self._websocket,
        )

        self._manager.register(
            subscription,
        )

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
        Dispatch a streamed tick message to
        its subscription.
        """

        subscription = message.get(
            "subscription",
            {},
        )

        subscription_id = subscription.get(
            "id",
        )

        if subscription_id is None:
            return False

        tick = TickResponse.model_validate(
            message,
        ).tick

        return await self._manager.dispatch(
            subscription_id,
            tick,
        )
