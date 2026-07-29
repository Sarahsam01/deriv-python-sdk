import asyncio

from deriv_sdk.logger import configure_logger
from deriv_sdk.transport.messages import PingRequest
from deriv_sdk.transport.websocket import WebSocketClient


async def main():
    configure_logger()

    client = WebSocketClient()

    await client.connect()

    print("Sending ping...")

    response = await client.request(
        PingRequest().to_dict(),
        expected="ping",
    )

    print()
    print("Response received:")
    print(response)

    await asyncio.sleep(2)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
