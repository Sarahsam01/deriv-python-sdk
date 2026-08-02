"""
===========================================================
Deriv Python SDK

Request ID Generator

Responsibilities
----------------
• Generate unique request identifiers
• Support custom ID generation
• Centralize request ID creation

Version : 1.0
===========================================================
"""

from __future__ import annotations

from typing import Protocol
from uuid import uuid4


class RequestIdGenerator(Protocol):
    """
    Protocol for request ID generators.
    """

    def generate(self) -> str:
        """
        Generate a unique request identifier.
        """
        ...


class UUIDRequestIdGenerator:
    """
    Default UUID4-based request ID generator.
    """

    def generate(self) -> str:
        """
        Return a new UUID4 string.
        """
        return str(uuid4())

    def __call__(self) -> str:
        """
        Convenience callable interface.
        """
        return self.generate()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
