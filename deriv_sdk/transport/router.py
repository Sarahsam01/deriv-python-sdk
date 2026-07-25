"""
===========================================================
Deriv SDK

Message Router

Routes incoming WebSocket messages.

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any

from deriv_sdk.logger import get_logger


class MessageRouter:
    """
    Routes incoming messages to registered handlers.
    """

    def __init__(self) -> None:
        self._logger = get_logger(__name__)
        self._handlers: dict[str, list[Callable[[dict[str, Any]], None]]] = defaultdict(
            list
        )

    def register(
        self,
        message_type: str,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:
        """
        Register a handler for a message type.
        """
        self._handlers[message_type].append(handler)

        self._logger.info(
            "Handler registered",
            message_type=message_type,
        )

    def unregister(
        self,
        message_type: str,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:
        """
        Remove a registered handler.
        """
        if handler in self._handlers[message_type]:
            self._handlers[message_type].remove(handler)

            self._logger.info(
                "Handler removed",
                message_type=message_type,
            )

    def dispatch(
        self,
        message: dict[str, Any],
    ) -> None:
        """
        Dispatch an incoming message.
        """
        message_type = message.get("msg_type")

        if not message_type:
            self._logger.warning(
                "Message has no msg_type",
            )
            return

        handlers = self._handlers.get(message_type, [])

        if not handlers:
            self._logger.warning(
                "No handlers registered",
                message_type=message_type,
            )
            return

        self._logger.info(
            "Dispatching message",
            message_type=message_type,
            handlers=len(handlers),
        )

        for handler in handlers:
            handler(message)
