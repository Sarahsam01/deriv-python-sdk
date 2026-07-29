"""
===========================================================
Deriv SDK

Client

Main SDK entry point.

Version : 1.0.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .auth.models import Account
from .config import SDKConfig
from .version import __version__

if TYPE_CHECKING:
    from .auth.service import AuthService
    from .market.service import MarketService
    from .trading.buy_service import BuyService
    from .trading.contract_service import ContractService
    from .trading.proposal_service import ProposalService
    from .transport.websocket import WebSocketClient


@dataclass(slots=True)
class DerivClient:
    """
    Main entry point for the Deriv SDK.

    This class owns the WebSocket connection and exposes all
    SDK services through a single interface.
    """

    config: SDKConfig = field(default_factory=SDKConfig)

    #
    # Transport
    #

    websocket: WebSocketClient = field(init=False)

    #
    # Core services
    #

    auth: AuthService = field(init=False)
    market: MarketService = field(init=False)

    #
    # Trading services
    #

    proposal: ProposalService = field(init=False)
    buy: BuyService = field(init=False)
    contract: ContractService = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the SDK transport layer and all services.
        """

        #
        # Deferred imports prevent circular dependencies.
        #

        from .auth.service import AuthService
        from .market.service import MarketService
        from .trading.buy_service import BuyService
        from .trading.contract_service import ContractService
        from .trading.proposal_service import ProposalService
        from .transport.websocket import WebSocketClient

        #
        # Transport
        #

        self.websocket = WebSocketClient(self.config)

        #
        # Core services
        #

        self.auth = AuthService(
            websocket=self.websocket,
            config=self.config,
        )

        self.market = MarketService(
            websocket=self.websocket,
        )

        #
        # Trading services
        #

        self.proposal = ProposalService(
            websocket=self.websocket,
        )

        self.buy = BuyService(
            websocket=self.websocket,
        )

        self.contract = ContractService(
            websocket=self.websocket,
        )

        #
        # Register streaming callbacks
        #

        self.websocket.register_market_service(
            self.market,
        )

    @property
    def version(self) -> str:
        """
        SDK version.
        """
        return __version__

    @property
    def connected(self) -> bool:
        """
        Whether the WebSocket connection is active.
        """
        return self.websocket.connected

    @property
    def authorized(self) -> bool:
        """
        Whether the client has been authenticated.
        """
        return self.auth.authorized

    async def connect(self) -> None:
        """
        Connect to the Deriv WebSocket API.
        """
        await self.websocket.connect()

    async def disconnect(self) -> None:
        """
        Disconnect from the Deriv WebSocket API.
        """
        await self.websocket.disconnect()

    async def authorize(self) -> Account:
        """
        Authenticate using the configured API token.

        Returns
        -------
        Account
            The authenticated Deriv account.
        """
        return await self.auth.authorize()

    async def close(self) -> None:
        """
        Close the SDK client.

        This is an alias for :meth:`disconnect`.
        """
        await self.disconnect()

    async def __aenter__(self) -> DerivClient:
        """
        Support asynchronous context management.
        """
        await self.connect()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object | None,
    ) -> None:
        """
        Ensure the connection is closed when leaving an
        async context manager.
        """
        await self.close()

    def __repr__(self) -> str:
        """
        Developer-friendly representation.
        """
        return (
            f"{self.__class__.__name__}("
            f"version='{self.version}', "
            f"connected={self.connected}, "
            f"authorized={self.authorized})"
        )
