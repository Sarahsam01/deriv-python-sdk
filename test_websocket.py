import asyncio

from deriv_sdk.logger import configure_logger
from deriv_sdk.transport.messages import PingRequest
from deriv_sdk.transport.router import MessageRouter
from deriv_sdk.transport.websocket import WebSocketClient


def on_ping(message):
    print("Router received:")
    print(message)


async def main():
    configure_logger()

    router = MessageRouter()
    router.register("ping", on_ping)

    client = WebSocketClient(router=router)

    await client.connect()

    await client.send(PingRequest().to_dict())

    await asyncio.sleep(5)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
