"""
===========================================================
Deriv SDK

Base Model

Shared functionality for all SDK models.

Version : 2.1.0
===========================================================
"""

from __future__ import annotations

from typing import Any, Self


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
        Convert this model into a dictionary.

        Works for all SDK models that store their data as
        instance attributes.
        """
        return dict(vars(self))
