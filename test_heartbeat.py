import asyncio

from deriv_sdk.logger import configure_logger
from deriv_sdk.transport.heartbeat import Heartbeat


async def fake_sender(message):
    print("SENT:", message)


async def main():
    configure_logger()

    heartbeat = Heartbeat(
        sender=fake_sender,
        interval=2,
    )

    await heartbeat.start()

    await asyncio.sleep(7)

    await heartbeat.stop()


if __name__ == "__main__":
    asyncio.run(main())