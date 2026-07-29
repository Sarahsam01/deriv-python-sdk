import asyncio

from deriv_sdk import DerivClient


async def main():
    client = DerivClient()

    await client.connect()
    await client.authorize()

    symbols = await client.market.active_symbols()

    print()
    print(f"Total Symbols: {len(symbols)}")
    print()

    for symbol in symbols[:10]:
        print(f"{symbol.symbol:<15}{symbol.display_name}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
