"""
===========================================================
Deriv SDK

Configuration

Loads and validates SDK configuration.

Version : 0.1.0
===========================================================
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .constants import DEFAULT_ENVIRONMENT, DEFAULT_TIMEOUT

load_dotenv()


@dataclass(slots=True)
class SDKConfig:
    """
    SDK connection configuration.

    Parameters
    ----------
    app_id:
        Deriv application id used to build the WebSocket URL.
    api_token:
        Optional Deriv API token for authenticated calls.
    environment:
        Logical environment label, usually ``demo`` or ``live``.
    timeout:
        Default timeout value used by callers that opt into config defaults.
    """

    app_id: str = os.getenv("DERIV_APP_ID", "")
    api_token: str = os.getenv("DERIV_API_TOKEN", "")
    environment: str = os.getenv(
        "DERIV_ENV",
        DEFAULT_ENVIRONMENT,
    )
    timeout: int = DEFAULT_TIMEOUT

    @property
    def websocket_url(self) -> str:
        """Return the Deriv WebSocket URL for the configured app id."""
        return f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"

    @property
    def is_demo(self) -> bool:
        """Return ``True`` when the configured environment is demo."""
        return self.environment.lower() == "demo"

    @property
    def is_live(self) -> bool:
        """Return ``True`` when the configured environment is live."""
        return self.environment.lower() == "live"

    def validate(self) -> None:
        """
        Validate required configuration values.

        Raises
        ------
        ValueError
            If ``app_id`` or ``api_token`` is missing.
        """
        if not self.app_id:
            raise ValueError("DERIV_APP_ID is missing.")

        if not self.api_token:
            raise ValueError("DERIV_API_TOKEN is missing.")
