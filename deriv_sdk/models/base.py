"""
===========================================================
Deriv SDK

Base Model

Shared functionality for all SDK models.

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Self, TypeVar

T = TypeVar("T", bound="BaseModel")


class BaseModel:
    """
    Base class for all SDK models.

    Provides serialization helpers while allowing each
    model to implement its own API parsing logic.
    """

    @classmethod
    def from_api(
        cls,
        response: dict[str, Any],
    ) -> Self:
        """
        Create a model from a Deriv API response.

        Must be implemented by subclasses.
        """
        raise NotImplementedError(
            f"{cls.__name__}.from_api() has not been implemented."
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the model into a dictionary.
        """
        return asdict(self)
