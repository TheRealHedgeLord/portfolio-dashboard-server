import time
import asyncio

from decimal import Decimal

from evm import EVM
from dapps.gmx import GMX
from dapps.gmx.gm import SupportedMarkets, MARKETS
from state.relational import RelationalDatabase
from state.relational.sql import Query

_database = RelationalDatabase()


async def _track_one_market(chain: str, market_symbol: SupportedMarkets) -> None:
    market = MARKETS[chain][market_symbol]
    table = "GM_{}_{}".format(chain, market["market_prop"][0])
    if table not in _database.get_all_tables():
        _database.write(
            Query.create_table(
                table,
                {
                    "timestamp": "integer",
                    "long_token_amount": "decimal",
                    "short_token_amount": "decimal",
                },
            )
        )
    evm = EVM.get_chain(chain)
    gmx = GMX(evm)
    long_token_amount, short_token_amount = await gmx.get_gm_withdraw_amount_out(
        Decimal("1"), market_symbol
    )
    timestamp = int(time.time())
    _database.write(
        Query.insert_row(
            table,
            {
                "timestamp": timestamp,
                "long_token_amount": long_token_amount,
                "short_token_amount": short_token_amount,
            },
        )
    )


async def track_all_markets() -> None:
    tasks = []
    for chain in MARKETS:
        for market in MARKETS[chain]:
            tasks.append(_track_one_market(chain, market))
    await asyncio.gather(*tasks)


methods = {"track_all_markets": track_all_markets}
