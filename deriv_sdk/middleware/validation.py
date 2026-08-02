"""
===========================================================
Deriv Python SDK

Validation Middleware

Responsibilities
----------------
• Validate outgoing requests
• Validate incoming responses
• Validate expected message types
• Provide a centralized validation layer

Version : 2.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.middleware.base import Middleware
from deriv_sdk.request.context import RequestContext


class ValidationMiddleware(Middleware):
    """
    Middleware responsible for validating requests and
    responses.

    Validation is intentionally lightweight in Version 2.
    More advanced schema validation can be added later.
    """

    # =====================================================
    # Request Validation
    # =====================================================

    async def before_request(
        self,
        context: RequestContext,
    ) -> None:
        """
        Validate the outgoing request.
        """

        payload = context.payload

        if not isinstance(payload, dict):
            raise TypeError("Request payload must be a dictionary.")

        if not payload:
            raise ValueError("Request payload cannot be empty.")

    # =====================================================
    # Response Validation
    # =====================================================

    async def after_response(
        self,
        context: RequestContext,
    ) -> None:
        """
        Validate the incoming response.
        """

        response = context.response

        if response is None:
            raise ValueError("Response cannot be None.")

        if not isinstance(response, dict):
            raise TypeError("Response must be a dictionary.")

        # ----------------------------------------------
        # API Error Response
        # ----------------------------------------------

        if "error" in response:
            return

        # ----------------------------------------------
        # Expected msg_type Validation
        # ----------------------------------------------

        expected = context.options.expected_msg_type

        if expected is None:
            return

        actual = response.get("msg_type")

        if actual != expected:
            raise ValueError(
                f"Unexpected response msg_type: expected {expected!r}, got {actual!r}."
            )

    # =====================================================
    # Exception Processing
    # =====================================================

    async def on_exception(
        self,
        context: RequestContext,
    ) -> None:
        """
        Validation middleware does not modify exceptions.

        This hook exists for future enhancements such as
        exception normalization.
        """
        return None

    # =====================================================
    # Helpers
    # =====================================================

    @staticmethod
    def require(
        payload: dict[str, Any],
        *fields: str,
    ) -> None:
        """
        Ensure required fields exist.

        Example
        -------
        ValidationMiddleware.require(
            payload,
            "proposal",
            "amount",
            "symbol",
        )
        """

        missing = [field for field in fields if field not in payload]

        if missing:
            raise ValueError("Missing required fields: " + ", ".join(missing))

    # =====================================================
    # Representation
    # =====================================================

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
