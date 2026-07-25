"""
===========================================================
Deriv SDK

Authentication Models

Typed models representing the Deriv authorize response.

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class Account(BaseModel):
    """Authenticated account information."""

    model_config = ConfigDict(extra="allow")

    loginid: str
    currency: str
    balance: float
    email: str | None = None
    fullname: str | None = None
    is_virtual: bool | None = None


class AuthorizeResponse(BaseModel):
    """Authorize response returned by Deriv."""

    model_config = ConfigDict(extra="allow")

    echo_req: dict[str, Any]
    msg_type: str
    authorize: Account