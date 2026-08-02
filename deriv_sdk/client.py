"""
===========================================================
Deriv Python SDK

High-Level Client

Responsibilities
----------------
• Own SDK configuration
• Create transport
• Create Request Engine
• Create and manage services
• Manage SDK lifecycle
• Expose a simple, high-level API

Version : 3.2
===========================================================
"""

from __future__ import annotations

from types import TracebackType
from typing import Any, cast

from deriv_sdk.auth.service import AuthService
from deriv_sdk.config import SDKConfig
from deriv_sdk.market.service import MarketService
from deriv_sdk.request.engine import RequestEngine
from deriv_sdk.trading.balance_service import BalanceService
from deriv_sdk.trading.buy_service import BuyService
from deriv_sdk.trading.contract_service import ContractService
from deriv_sdk.trading.proposal_service import ProposalService
from deriv_sdk.trading.transaction_service import TransactionService
from deriv_sdk.transport.websocket import WebSocketClient


class DerivClient:
    """
    High-level SDK client.

    This is the main entry point for the SDK.

    Example
    -------
    >>> client = DerivClient(
    ...     app_id="1089",
    ...     api_token="YOUR_TOKEN",
    ... )
    ...
    >>> await client.start()
    >>> symbols = await client.market.active_symbols()
    >>> await client.close()
    """

    def __init__(
        self,
        *,
        app_id: str,
        api_token: str | None = None,
        config: SDKConfig | None = None,
    ) -> None:
        """
        Initialize the SDK.

        No network activity occurs here.
        """

        # ==================================================
        # Configuration
        # ==================================================

        if config is None:
            config = SDKConfig(
                app_id=app_id,
                api_token=api_token or "",
            )

        self._config = config

        # ==================================================
        # Transport
        # ==================================================

        self._transport = WebSocketClient(config)

        # ==================================================
        # Request Engine
        # ==================================================

        self._request_engine = RequestEngine(
            self._transport,
        )

        # ==================================================
        # Service Registry
        # ==================================================

        self._services: dict[str, Any] = {}

        self._register_service(
            "auth",
            AuthService(self._request_engine),
        )

        market = MarketService(self._request_engine)
        self._register_service("market", market)
        self._transport.register_market_service(market)

        self._register_service("proposal", ProposalService(self._request_engine))
        self._register_service("buy", BuyService(self._request_engine))
        self._register_service("balance", BalanceService(self._request_engine))
        self._register_service("contract", ContractService(self._request_engine))
        self._register_service("transaction", TransactionService(self._request_engine))

        # ==================================================
        # Client State
        # ==================================================

        self._started = False

    # ======================================================
    # Service Registry
    # ======================================================

    def _register_service(
        self,
        name: str,
        service: Any,
    ) -> None:
        """
        Register a service.
        """

        if name in self._services:
            raise ValueError(f"Service '{name}' is already registered.")

        self._services[name] = service

    def _service(
        self,
        name: str,
    ) -> Any:
        """
        Retrieve a registered service.
        """

        try:
            return self._services[name]

        except KeyError as exc:
            raise AttributeError(f"Service '{name}' is not registered.") from exc

    # ======================================================
    # Lifecycle
    # ======================================================

    async def start(self) -> None:
        """
        Start the SDK.

        Steps
        -----
        1. Connect
        2. Authorize
        3. Ready
        """

        if self._started:
            return

        try:
            await self._transport.connect()

            if self._config.api_token:
                await self.auth.authorize(
                    self._config.api_token,
                )

            self._started = True

        except Exception:
            try:
                await self._transport.close()

            finally:
                self._started = False

            raise

    async def close(self) -> None:
        """
        Gracefully shut down the SDK.
        """

        if self._started or self._transport.connected:
            await self._transport.close()

        self._started = False

    # ======================================================
    # Async Context Manager
    # ======================================================

    async def __aenter__(self) -> DerivClient:
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.close()

    # ======================================================
    # Properties
    # ======================================================

    @property
    def config(self) -> SDKConfig:
        """
        SDK configuration.
        """
        return self._config

    @property
    def transport(self) -> WebSocketClient:
        """
        Shared WebSocket transport.
        """
        return self._transport

    @property
    def request_engine(self) -> RequestEngine:
        """
        Shared Request Engine.

        All SDK services communicate through
        this engine.
        """
        return self._request_engine

    @property
    def started(self) -> bool:
        """
        Whether the SDK has been started.
        """
        return self._started

    @property
    def connected(self) -> bool:
        """
        Whether the transport is connected.
        """
        return self._transport.connected

    @property
    def authorized(self) -> bool:
        """
        Whether the session has been authorized.
        """
        return self.auth.authorized

    # ======================================================
    # Services
    # ======================================================

    @property
    def auth(self) -> AuthService:
        """
        Authentication service.
        """
        return cast(AuthService, self._service("auth"))

    @property
    def market(self) -> MarketService:
        """
        Market service.
        """
        return cast(MarketService, self._service("market"))

    @property
    def proposal(self) -> ProposalService:
        """
        Proposal service.
        """
        return cast(ProposalService, self._service("proposal"))

    @property
    def buy(self) -> BuyService:
        """
        Buy service.
        """
        return cast(BuyService, self._service("buy"))

    @property
    def balance(self) -> BalanceService:
        """
        Balance service.
        """
        return cast(BalanceService, self._service("balance"))

    @property
    def contract(self) -> ContractService:
        """
        Contract service.
        """
        return cast(ContractService, self._service("contract"))

    @property
    def transaction(self) -> TransactionService:
        """
        Transaction service.
        """
        return cast(TransactionService, self._service("transaction"))

    # ======================================================
    # Representation
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"started={self.started}, "
            f"connected={self.connected}, "
            f"authorized={self.authorized}"
            f")"
        )
