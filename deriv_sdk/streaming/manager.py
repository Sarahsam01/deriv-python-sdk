"""
===========================================================
Deriv SDK

Streaming Subscription Manager

Responsibilities
----------------
• Register subscriptions
• Remove subscriptions
• Route streaming messages
• Lookup subscriptions

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.logger import get_logger
from deriv_sdk.streaming.subscription import Subscription


class SubscriptionManager:
    """
    Manages all active streaming subscriptions.
    """

    def __init__(self) -> None:

        self._logger = get_logger(__name__)

        self._subscriptions: dict[
            str,
            Subscription[Any],
        ] = {}

    # =====================================================
    # Registration
    # =====================================================

    def register(
        self,
        subscription: Subscription[Any],
    ) -> None:
        """
        Register a new subscription.
        """

        self._subscriptions[subscription.id] = subscription

        self._logger.debug(
            "Subscription registered.",
            subscription_id=subscription.id,
        )

    # =====================================================
    # Removal
    # =====================================================

    def unregister(
        self,
        subscription_id: str,
    ) -> None:
        """
        Remove a subscription.
        """

        self._subscriptions.pop(
            subscription_id,
            None,
        )

        self._logger.debug(
            "Subscription removed.",
            subscription_id=subscription_id,
        )

    # =====================================================
    # Lookup
    # =====================================================

    def get(
        self,
        subscription_id: str,
    ) -> Subscription[Any] | None:
        """
        Retrieve a subscription by ID.
        """

        return self._subscriptions.get(subscription_id)

    def exists(
        self,
        subscription_id: str,
    ) -> bool:
        """
        Check whether a subscription exists.
        """

        return subscription_id in self._subscriptions

    @property
    def count(self) -> int:
        """
        Number of active subscriptions.
        """

        return len(self._subscriptions)

    # =====================================================
    # Routing
    # =====================================================

    async def dispatch(
        self,
        subscription_id: str,
        item: Any,
    ) -> bool:
        """
        Route a streamed item to its subscription.

        Returns
        -------
        bool
            True if a subscription was found.
        """

        subscription = self.get(subscription_id)

        if subscription is None:
            self._logger.warning(
                "Unknown subscription.",
                subscription_id=subscription_id,
            )

            return False

        await subscription.put(item)

        return True

    # =====================================================
    # Cleanup
    # =====================================================

    def clear(self) -> None:
        """
        Remove all subscriptions.
        """

        self._subscriptions.clear()

        self._logger.info("All subscriptions cleared.")

    def __len__(self) -> int:
        return self.count

    def __contains__(
        self,
        subscription_id: str,
    ) -> bool:
        return self.exists(subscription_id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(subscriptions={self.count})"
