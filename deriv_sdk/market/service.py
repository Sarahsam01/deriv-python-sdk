"""
===========================================================
Deriv SDK

Market Service

Responsibilities
----------------
• Active Symbols
• Historical Market Data
• Trading Times
• Contracts For
• Tick Streaming
• Request validation
• Response validation

Version : 3.0.0
===========================================================
"""

from __future__ import annotations

from typing import Any, Protocol

from deriv_sdk.logger import get_logger
from deriv_sdk.market.exceptions import MarketError
from deriv_sdk.market.models import (
    ActiveSymbol,
    CandleHistory,
    ContractsFor,
    TickHistory,
)
from deriv_sdk.market.requests import (
    ActiveSymbolsRequest,
    ContractsForRequest,
    TicksHistoryRequest,
    TradingTimesRequest,
)
from deriv_sdk.market.responses import (
    ActiveSymbolsResponse,
    ContractsForResponse,
    TicksHistoryResponse,
    TradingTimesResponse,
)
from deriv_sdk.streaming.manager import SubscriptionManager
from deriv_sdk.streaming.models import Tick
from deriv_sdk.streaming.subscription import Subscription
from deriv_sdk.streaming.tick_stream import TickStream


class WebSocketProtocol(Protocol):
    """
    Protocol describing the websocket interface required by
    MarketService.
    """

    async def request(
        self,
        message: dict[str, Any],
        *,
        expected: str,
    ) -> dict[str, Any]: ...


class MarketService:
    """
    Provides access to Deriv market endpoints.
    """

    def __init__(
        self,
        websocket: WebSocketProtocol,
    ) -> None:
        self._websocket = websocket

        self._logger = get_logger(__name__)

        self._subscriptions = SubscriptionManager()

        self._tick_stream = TickStream(
            websocket=self._websocket,
            manager=self._subscriptions,
        )

    # =====================================================
    # Internal Helpers
    # =====================================================

    @staticmethod
    def _raise_market_error(
        response: dict[str, Any],
    ) -> None:
        """
        Raise MarketError if the API response contains an error.
        """

        if "error" not in response:
            return

        error = response["error"]

        raise MarketError(
            f"{error.get('code', 'UnknownError')}: "
            f"{error.get('message', 'Unknown error')}"
        )

    # =====================================================
    # Active Symbols
    # =====================================================

    async def active_symbols(
        self,
        brief: bool = True,
    ) -> list[ActiveSymbol]:
        """
        Retrieve active trading symbols.
        """

        payload = ActiveSymbolsRequest(
            brief=brief,
        ).to_dict()

        self._logger.debug(
            "Sending active_symbols request.",
            payload=payload,
        )

        response = await self._websocket.request(
            payload,
            expected="active_symbols",
        )

        self._raise_market_error(response)

        result = ActiveSymbolsResponse.model_validate(response)

        self._logger.info(
            "Retrieved active symbols.",
            count=result.count,
        )

        return result.active_symbols

    # =====================================================
    # Historical Market Data
    # =====================================================

    async def ticks_history(
        self,
        symbol: str,
        *,
        count: int = 100,
        start: int | None = None,
        end: int | str = "latest",
        granularity: int | None = None,
        style: str = "ticks",
    ) -> TickHistory | CandleHistory:
        """
        Retrieve historical market data.
        """

        payload = TicksHistoryRequest(
            ticks_history=symbol,
            count=count,
            start=start,
            end=end,
            granularity=granularity,
            style=style,
        ).to_dict()

        self._logger.debug(
            "Sending ticks_history request.",
            payload=payload,
        )

        response = await self._websocket.request(
            payload,
            expected="history",
        )

        self._raise_market_error(response)

        result = TicksHistoryResponse.parse_history(response)

        if isinstance(result, TickHistory):
            self._logger.info(
                "Retrieved historical ticks.",
                count=result.count,
            )
        else:
            self._logger.info(
                "Retrieved historical candles.",
                count=result.count,
            )

        return result

    # =====================================================
    # Trading Times
    # =====================================================

    async def trading_times(
        self,
        date: str | None = None,
    ) -> TradingTimesResponse:
        """
        Retrieve trading times.
        """

        payload = TradingTimesRequest(
            date=date,
        ).to_dict()

        response = await self._websocket.request(
            payload,
            expected="trading_times",
        )

        self._raise_market_error(response)

        data = response.get("trading_times", response)

        result = TradingTimesResponse.model_validate(data)

        self._logger.info(
            "Retrieved trading times.",
            markets=len(result.markets),
        )

        return result

    # =====================================================
    # Contracts For
    # =====================================================

    async def contracts_for(
        self,
        symbol: str,
        *,
        currency: str | None = None,
        product_type: str = "basic",
    ) -> ContractsFor:
        """
        Retrieve available contracts for a market symbol.
        """

        payload = ContractsForRequest(
            symbol=symbol,
            currency=currency,
            product_type=product_type,
        ).to_dict()

        response = await self._websocket.request(
            payload,
            expected="contracts_for",
        )

        self._raise_market_error(response)

        data = response.get("contracts_for", response)

        result = ContractsForResponse.model_validate(data)

        self._logger.info(
            "Retrieved available contracts.",
            count=result.count,
        )

        return result

    # =====================================================
    # Tick Streaming
    # =====================================================

    async def subscribe_ticks(
        self,
        symbol: str,
    ) -> Subscription[Tick]:
        """
        Subscribe to live market ticks.
        """

        return await self._tick_stream.subscribe(
            symbol=symbol,
        )

    async def dispatch_stream(
        self,
        message: dict[str, Any],
    ) -> bool:
        """
        Dispatch streaming messages.

        Returns
        -------
        bool
            True if the message was handled.
        """

        if message.get("msg_type") != "tick":
            return False

        return await self._tick_stream.dispatch(message)

    # =====================================================
    # Properties
    # =====================================================

    @property
    def subscriptions(self) -> SubscriptionManager:
        """
        Active subscription manager.
        """

        return self._subscriptions
