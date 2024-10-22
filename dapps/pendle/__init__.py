from dapps.pendle.market import PendleMarket


async def get_market(chain: str, market_address: str) -> PendleMarket:
    market = PendleMarket(chain, market_address)
    await market.initialize()
    return market
