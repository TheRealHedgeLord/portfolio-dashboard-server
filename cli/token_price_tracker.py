import time
import json

from os import environ

from state.relational import RelationalDatabase
from state.relational.sql import Query
from web2.coingecko import CoinGecko

_coin_gecko_client = CoinGecko(environ["COINGECKO_API_KEY"])
_database = RelationalDatabase()


def _create_token_table_if_not_exist(table_name: str) -> None:
    if table_name not in _database.get_all_tables():
        _database.write(
            Query.create_table(
                table_name,
                {"timestamp": "integer", "price": "decimal", "market_cap": "decimal"},
            )
        )


async def track_token(symbol: str, reference: str, reference_config_json: str) -> None:
    reference_config = json.loads(reference_config_json)
    table_name = f"tracked_tokens"
    _create_token_table_if_not_exist(table_name)
    table = _database.read(Query.get_table(table_name))
    symbols = table.get_column("symbol")
    if symbol in symbols:
        _database.write(
            Query.update_table(
                table_name,
                {"symbol": symbol},
                {"reference": reference, "reference_config": reference_config},
            )
        )
    else:
        _database.write(
            Query.insert_row(
                table_name,
                {
                    "symbol": symbol,
                    "reference": reference,
                    "reference_config": reference_config,
                },
            )
        )


async def track_all_tokens() -> None:
    coingecko_tokens = _database.read(
        Query.get_table(
            "tracked_tokens",
            columns=["symbol", "reference_config"],
            match_values={"reference": "coingecko"},
        )
    )
    token_prices = await _coin_gecko_client.get_token_data(
        *[
            config["token_id"]  # type: ignore
            for config in coingecko_tokens.get_column("reference_config")
        ]
    )
    timestamp = int(time.time())
    for i in range(coingecko_tokens.row_count):
        symbol = coingecko_tokens.get_column("symbol")[i]
        table = f"tracked_token_{symbol}"
        price, market_cap = token_prices[i]
        _database.write(
            Query.insert_row(
                table,
                {"timestamp": timestamp, "price": price, "market_cap": market_cap},
            )
        )


methods = {"track_token": track_token, "track_all_tokens": track_all_tokens}
