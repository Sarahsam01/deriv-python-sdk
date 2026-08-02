"""
===========================================================
Deriv Python SDK

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

Version : 4.0
===========================================================
"""

from __future__ import annotations

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
from deriv_sdk.services.base import (
    BaseService,
    RequestEngineProtocol,
    RequestTransportProtocol,
)
from deriv_sdk.streaming.manager import SubscriptionManager
from deriv_sdk.streaming.models import Tick
from deriv_sdk.streaming.subscription import Subscription
from deriv_sdk.streaming.tick_stream import TickStream


class MarketService(BaseService):
    """
    High-level service exposing Deriv market endpoints.
    """

    def __init__(
        self,
        engine: RequestEngineProtocol | RequestTransportProtocol,
    ) -> None:
        super().__init__(engine)

        self._logger = get_logger(__name__)

        self._subscriptions = SubscriptionManager()

        self._tick_stream = TickStream(
            websocket=self.engine,
            manager=self._subscriptions,
        )

    # =====================================================
    # Internal Helpers
    # =====================================================

    @staticmethod
    def _raise_market_error(
        response: dict,
    ) -> None:
        """
        Raise MarketError if the API returned an error.
        """

        error = response.get("error")

        if error is None:
            return

        raise MarketError(
            f"{error.get('code', 'UnknownError')}: "
            f"{error.get('message', 'Unknown error')}"
        )

    # =====================================================
    # Active Symbols
    # =====================================================

    async def active_symbols(
        self,
        *,
        brief: bool = True,
    ) -> list[ActiveSymbol]:
        """
        Retrieve active trading symbols.
        """

        payload = ActiveSymbolsRequest(
            brief=brief,
        ).to_dict()

        self._logger.debug(
            "Requesting active symbols.",
            payload=payload,
        )

        response = await self.request(
            payload,
            expected="active_symbols",
            service_name="market",
            endpoint="active_symbols",
        )

        self._raise_market_error(response)

        result = ActiveSymbolsResponse.model_validate(response)

        self._logger.info(
            "Retrieved active symbols.",
            count=result.count,
        )

        return result.active_symbols

    # =====================================================
    # Historical Data
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
            "Requesting tick history.",
            payload=payload,
        )

        expected = "candles" if style == "candles" else "history"

        response = await self.request(
            payload,
            expected=expected,
            service_name="market",
            endpoint="ticks_history",
        )

        self._raise_market_error(response)

        result = TicksHistoryResponse.parse_history(
            response,
        )

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

        self._logger.debug(
            "Requesting trading times.",
            payload=payload,
        )

        response = await self.request(
            payload,
            expected="trading_times",
            service_name="market",
            endpoint="trading_times",
        )

        self._raise_market_error(response)

        data = response.get(
            "trading_times",
            response,
        )

        result = TradingTimesResponse.model_validate(
            data,
        )

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
        Retrieve available contracts for a symbol.
        """

        payload = ContractsForRequest(
            symbol=symbol,
            currency=currency,
            product_type=product_type,
        ).to_dict()

        self._logger.debug(
            "Requesting contracts.",
            payload=payload,
        )

        response = await self.request(
            payload,
            expected="contracts_for",
            service_name="market",
            endpoint="contracts_for",
        )

        self._raise_market_error(response)

        data = response.get(
            "contracts_for",
            response,
        )

        result = ContractsForResponse.model_validate(
            data,
        )

        self._logger.info(
            "Retrieved contracts.",
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
        Subscribe to live ticks.
        """

        return await self._tick_stream.subscribe(
            symbol=symbol,
        )

    async def dispatch_stream(
        self,
        message: dict,
    ) -> bool:
        """
        Dispatch an incoming streaming message.

        Returns
        -------
        bool
            True if the message was processed.
        """

        if message.get("msg_type") != "tick":
            return False

        return await self._tick_stream.dispatch(
            message,
        )

    # =====================================================
    # Properties
    # =====================================================

    @property
    def subscriptions(self) -> SubscriptionManager:
        """
        Active subscription manager.
        """
        return self._subscriptions

    @property
    def tick_stream(self) -> TickStream:
        """
        Tick stream manager.
        """
        return self._tick_stream
