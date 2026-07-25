import asyncio

from deriv_sdk.config import SDKConfig
from deriv_sdk.logger import configure_logger
from deriv_sdk.transport.websocket import WebSocketClient


async def main():
    configure_logger()

    config = SDKConfig()

    client = WebSocketClient(config)

    print("Connected:", client.connected)

    await client.connect()

    print("Connected:", client.connected)

    await client.disconnect()

    print("Connected:", client.connected)


if __name__ == "__main__":
    asyncio.run(main())
