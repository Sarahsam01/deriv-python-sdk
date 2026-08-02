"""
===========================================================
Deriv SDK

Exception Hierarchy

Central exception hierarchy used throughout the SDK.

Version : 3.0.0
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
        if self.code is not None:
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


class RequestCancelledError(TransportError):
    """A request was cancelled before completion."""


class ClientClosedError(TransportError):
    """The client or transport was closed while work was pending."""


class ReconnectError(TransportError):
    """Automatic reconnection failed."""


class MessageRouterError(TransportError):
    """Message routing failure."""


# =========================================================
# Validation
# =========================================================


class ValidationError(DerivError):
    """Invalid request parameters."""


# =========================================================
# API
# =========================================================


class APIError(DerivError):
    """
    Base class for all errors returned by the Deriv API.
    """


class AuthenticationError(APIError):
    """Authentication failed."""


class AuthorizationError(APIError):
    """Authorization failed."""


class ProposalError(APIError):
    """Proposal request failed."""


class BuyError(APIError):
    """Buy request failed."""


class ContractError(APIError):
    """Contract request failed."""


class BalanceError(APIError):
    """Balance request failed."""


class RateLimitError(APIError):
    """API rate limit exceeded."""


class CircuitOpenError(DerivError):
    """A circuit breaker is open and rejected the request."""


class RetryExhaustedError(DerivError):
    """Retry attempts were exhausted."""


class SubscriptionError(DerivError):
    """Streaming subscription failure."""


# =========================================================
# Models
# =========================================================


class ParsingError(DerivError):
    """Unable to parse an API response."""
