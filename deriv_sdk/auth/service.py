"""
===========================================================
Deriv SDK

Authentication Service

Responsibilities
----------------
• Authorize with Deriv
• Store authenticated account
• Expose authorization status

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any, Protocol

from deriv_sdk.auth.models import Account, AuthorizeResponse
from deriv_sdk.transport.messages import AuthorizeRequest


class WebSocketProtocol(Protocol):
    """
    Protocol describing the websocket interface required by AuthService.
    """

    async def request(
        self,
        message: dict[str, Any],
        *,
        expected: str,
    ) -> dict[str, Any]: ...


class ConfigProtocol(Protocol):
    """
    Protocol describing the configuration required by AuthService.
    """

    api_token: str


class AuthService:
    """
    Authentication service.
    """

    def __init__(
        self,
        websocket: WebSocketProtocol,
        config: ConfigProtocol,
    ) -> None:
        self._websocket = websocket
        self._config = config

        self._authorized = False
        self._account: Account | None = None

    @property
    def authorized(self) -> bool:
        """
        True if authenticated.
        """
        return self._authorized

    @property
    def account(self) -> Account | None:
        """
        Authenticated account.
        """
        return self._account

    async def authorize(self) -> Account:
        """
        Authenticate using the configured API token.
        """

        message = AuthorizeRequest(self._config.api_token).to_dict()

        response: dict[str, Any] = await self._websocket.request(
            message,
            expected="authorize",
        )

        result = AuthorizeResponse.model_validate(response)

        self._authorized = True
        self._account = result.authorize

        return result.authorize
