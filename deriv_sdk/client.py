"""
===========================================================
Deriv SDK

Client

Main SDK entry point.

Version : 0.6.0
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

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
    Main SDK client.

    Acts as the primary entry point to all SDK services.
    """

    config: SDKConfig = field(default_factory=SDKConfig)

    websocket: WebSocketClient = field(init=False)

    #
    # Core Services
    #

    auth: AuthService = field(init=False)

    market: MarketService = field(init=False)

    #
    # Trading Services
    #

    proposal: ProposalService = field(init=False)

    buy: BuyService = field(init=False)

    contract: ContractService = field(init=False)

    def __post_init__(self) -> None:
        """
        Initialize the SDK transport and services.
        """

        from .auth.service import AuthService
        from .market.service import MarketService
        from .trading.buy_service import BuyService
        from .trading.contract_service import ContractService
        from .trading.proposal_service import ProposalService
        from .transport.websocket import WebSocketClient

        #
        # Transport
        #

        self.websocket = WebSocketClient(
            self.config,
        )

        #
        # Core Services
        #

        self.auth = AuthService(
            self.websocket,
            self.config,
        )

        self.market = MarketService(
            self.websocket,
        )

        #
        # Trading Services
        #

        self.proposal = ProposalService(
            self.websocket,
        )

        self.buy = BuyService(
            self.websocket,
        )

        self.contract = ContractService(
            self.websocket,
        )

        #
        # Register streaming handlers
        #

        self.websocket.register_market_service(
            self.market,
        )

    @property
    def version(self) -> str:
        """
        Return the SDK version.
        """
        return __version__

    @property
    def connected(self) -> bool:
        """
        Return True if connected.
        """
        return self.websocket.connected

    @property
    def authorized(self) -> bool:
        """
        Return True if authorized.
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

    async def authorize(self):
        """
        Authorize using the configured API token.
        """
        return await self.auth.authorize()

    async def close(self) -> None:
        """
        Alias for disconnect().
        """
        await self.disconnect()

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
