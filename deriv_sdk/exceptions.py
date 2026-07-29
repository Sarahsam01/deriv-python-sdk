"""
===========================================================
Deriv SDK

Exception Hierarchy

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any


class DerivError(Exception):
    """
    Base exception for all SDK errors.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)

        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


# =========================================================
# Configuration
# =========================================================


class ConfigurationError(DerivError):
    """Invalid SDK configuration."""


# =========================================================
# Transport
# =========================================================


class TransportError(DerivError):
    """Transport layer failure."""


class ConnectionError(TransportError):
    """Unable to establish a WebSocket connection."""


class TimeoutError(TransportError):
    """A request timed out."""


class ReconnectError(TransportError):
    """Automatic reconnection failed."""


class MessageRouterError(TransportError):
    """Message routing failure."""


# =========================================================
# Authentication
# =========================================================


class AuthenticationError(DerivError):
    """Authentication failed."""


class AuthorizationError(DerivError):
    """Authorization failed."""


# =========================================================
# Validation
# =========================================================


class ValidationError(DerivError):
    """Invalid request parameters."""


# =========================================================
# API
# =========================================================


class APIError(DerivError):
    """Deriv API returned an error."""


class ProposalError(APIError):
    """Proposal request failed."""


class BuyError(APIError):
    """Buy request failed."""


class ContractError(APIError):
    """Contract request failed."""


class BalanceError(APIError):
    """Balance request failed."""


class RateLimitError(APIError):
    """Rate limit exceeded."""


# =========================================================
# Models
# =========================================================


class ParsingError(DerivError):
    """Unable to parse an API response."""
