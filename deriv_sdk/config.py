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
    """SDK configuration."""

    app_id: str = os.getenv("DERIV_APP_ID", "")
    api_token: str = os.getenv("DERIV_API_TOKEN", "")
    environment: str = os.getenv(
        "DERIV_ENV",
        DEFAULT_ENVIRONMENT,
    )
    timeout: int = DEFAULT_TIMEOUT

    @property
    def websocket_url(self) -> str:
        return f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"

    @property
    def is_demo(self) -> bool:
        return self.environment.lower() == "demo"

    @property
    def is_live(self) -> bool:
        return self.environment.lower() == "live"

    def validate(self) -> None:
        if not self.app_id:
            raise ValueError("DERIV_APP_ID is missing.")

        if not self.api_token:
            raise ValueError("DERIV_API_TOKEN is missing.")
