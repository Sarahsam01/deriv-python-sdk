import asyncio

from deriv_sdk import DerivClient


async def main():
    client = DerivClient()

    await client.connect()

    account = await client.authorize()

    print(f"Login ID : {account.loginid}")
    print(f"Balance  : {account.balance}")
    print(f"Currency : {account.currency}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())