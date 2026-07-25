"""
===========================================================
Deriv SDK

Authentication Service

Responsibilities
----------------
• Authorize with Deriv
• Store authenticated account
• Expose authorization status

Version : 0.2.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.auth.models import Account, AuthorizeResponse
from deriv_sdk.transport.messages import AuthorizeRequest


class AuthService:
    """
    Authentication service.
    """

    def __init__(self, websocket, config) -> None:
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

        message = AuthorizeRequest(
            self._config.api_token
        ).to_dict()

        response: dict[str, Any] = await self._websocket.request(
            message,
            expected="authorize",
        )

        result = AuthorizeResponse.model_validate(response)

        self._authorized = True
        self._account = result.authorize

        return result.authorize