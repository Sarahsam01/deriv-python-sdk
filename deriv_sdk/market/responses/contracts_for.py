"""
===========================================================
Deriv SDK

Contracts For Response

Responsibilities
----------------
• Parse contracts_for responses

Version : 2.0.0
===========================================================
"""

from __future__ import annotations

from deriv_sdk.market.models import ContractsFor


class ContractsForResponse(ContractsFor):
    """
    Response returned by the Deriv contracts_for endpoint.

    Inherits the shared ContractsFor model so that
    the response layer contains no duplicated models.
    """

    pass