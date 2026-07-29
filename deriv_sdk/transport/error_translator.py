"""
===========================================================
Deriv SDK

API Error Translator

Version : 1.1.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from deriv_sdk.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BuyError,
    ContractError,
    ProposalError,
    RateLimitError,
)


def translate_api_error(
    error: dict[str, Any],
) -> APIError:
    """
    Translate a Deriv API error into a typed SDK exception.
    """

    code = str(error.get("code", ""))
    message = str(error.get("message", "Unknown API error."))

    mapping: dict[str, type[APIError]] = {
        "InvalidToken": AuthenticationError,
        "AuthorizationRequired": AuthorizationError,
        "RateLimit": RateLimitError,
        "InvalidProposal": ProposalError,
        "BuyValidationError": BuyError,
        "InvalidContract": ContractError,
    }

    exception_cls: type[APIError] = mapping.get(code, APIError)

    return exception_cls(
        message,
        code=code,
        details=error,
    )
