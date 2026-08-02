"""
===========================================================
Deriv Python SDK

Authentication Service

Responsibilities
----------------
• Authorize session
• Retrieve account information
• Manage authorization state

Version : 2.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.services.base import (
    BaseService,
    RequestEngineProtocol,
    RequestTransportProtocol,
)


class AuthService(BaseService):
    """
    Authentication service.
    """

    def __init__(
        self,
        engine: RequestEngineProtocol | RequestTransportProtocol,
    ) -> None:
        super().__init__(engine)

        self._authorized = False
        self._authorize_response: dict[str, Any] | None = None

    @property
    def authorized(self) -> bool:
        """
        Whether the session has been authorized.
        """
        return self._authorized

    @property
    def authorize_response(self) -> dict[str, Any] | None:
        """
        Raw authorize response.
        """
        return self._authorize_response

    async def authorize(
        self,
        token: str,
    ) -> dict[str, Any]:
        """
        Authorize the current session.
        """

        payload = {
            "authorize": token,
        }

        response = await self.request(
            payload,
            expected="authorize",
            service_name="auth",
            endpoint="authorize",
        )

        self._authorized = True
        self._authorize_response = response

        return response
