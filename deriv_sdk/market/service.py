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

Version : 2.5.0
===========================================================
"""

from __future__ import annotations

from typing import Any

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


class MarketService:
    """
    Provides access to Deriv market endpoints.
    """

    def __init__(self, websocket) -> None:
        self._websocket = websocket

        self._logger = get_logger(__name__)

        # Shared subscription manager
        self._subscriptions = SubscriptionManager()

        # Tick streaming service
        self._tick_stream = TickStream(
            websocket=self._websocket,
            manager=self._subscriptions,
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

        request = ActiveSymbolsRequest(
            brief=brief,
        )

        payload = request.to_dict()

        self._logger.debug(
            "Sending active_symbols request.",
            payload=payload,
        )

        response: dict[str, Any] = await self._websocket.request(
            payload,
            expected="active_symbols",
        )

        self._logger.debug(
            "Received active_symbols response.",
            response=response,
        )

        if "error" in response:
            error = response["error"]

            raise MarketError(
                f"{error.get('code', 'UnknownError')}: "
                f"{error.get('message', 'Unknown error')}"
            )

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

        request = TicksHistoryRequest(
            ticks_history=symbol,
            count=count,
            start=start,
            end=end,
            granularity=granularity,
            style=style,
        )

        payload = request.to_dict()

        self._logger.debug(
            "Sending ticks_history request.",
            payload=payload,
        )

        response: dict[str, Any] = await self._websocket.request(
            payload,
            expected="history",
        )

        self._logger.debug(
            "Received ticks_history response.",
            response=response,
        )

        if "error" in response:
            error = response["error"]

            raise MarketError(
                f"{error.get('code', 'UnknownError')}: "
                f"{error.get('message', 'Unknown error')}"
            )

        result = TicksHistoryResponse.model_validate(response)

        if isinstance(result, TickHistory):
            self._logger.info(
                "Retrieved historical ticks.",
                count=result.count,
            )

        elif isinstance(result, CandleHistory):
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

        request = TradingTimesRequest(
            date=date,
        )

        payload = request.to_dict()

        self._logger.debug(
            "Sending trading_times request.",
            payload=payload,
        )

        response: dict[str, Any] = await self._websocket.request(
            payload,
            expected="trading_times",
        )

        self._logger.debug(
            "Received trading_times response.",
            response=response,
        )

        if "error" in response:
            error = response["error"]

            raise MarketError(
                f"{error.get('code', 'UnknownError')}: "
                f"{error.get('message', 'Unknown error')}"
            )

        if "trading_times" in response:
            response = response["trading_times"]

        result = TradingTimesResponse.model_validate(response)

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

        request = ContractsForRequest(
            symbol=symbol,
            currency=currency,
            product_type=product_type,
        )

        payload = request.to_dict()

        self._logger.debug(
            "Sending contracts_for request.",
            payload=payload,
        )

        response: dict[str, Any] = await self._websocket.request(
            payload,
            expected="contracts_for",
        )

        self._logger.debug(
            "Received contracts_for response.",
            response=response,
        )

        if "error" in response:
            error = response["error"]

            raise MarketError(
                f"{error.get('code', 'UnknownError')}: "
                f"{error.get('message', 'Unknown error')}"
            )

        if "contracts_for" in response:
            response = response["contracts_for"]

        result = ContractsForResponse.model_validate(response)

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

        msg_type = message.get("msg_type")

        if msg_type == "tick":
            return await self._tick_stream.dispatch(message)

        return False

    # =====================================================
    # Properties
    # =====================================================

    @property
    def subscriptions(self) -> SubscriptionManager:
        """
        Active subscription manager.
        """

        return self._subscriptions