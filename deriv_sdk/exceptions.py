"""
===========================================================
Deriv SDK

Custom Exception Hierarchy

Version : 0.1.0
===========================================================
"""


class DerivError(Exception):
    """Base exception for all Deriv SDK errors."""


class ConfigurationError(DerivError):
    """Invalid SDK configuration."""


class ConnectionError(DerivError):
    """Connection to Deriv failed."""


class AuthenticationError(DerivError):
    """Authentication failed."""


class TransportError(DerivError):
    """Transport layer error."""


class ValidationError(DerivError):
    """Invalid request parameters."""


class MarketError(DerivError):
    """Market-related error."""


class ProposalError(DerivError):
    """Proposal request failed."""


class TradeError(DerivError):
    """Trading operation failed."""


class SubscriptionError(DerivError):
    """Subscription error."""


class ContractError(DerivError):
    """Contract monitoring error."""
