import asyncio

from decimal import Decimal

from state.relational import RelationalDatabase
from state.relational.sql import Query
from cli.portfolio.assets import Coin
from cli.portfolio.account import AccountCipher
from utils import add_to_dict


class CoinPortfolio:
    def __init__(self, passphrase: str) -> None:
        self.cipher = AccountCipher(passphrase)
        database = RelationalDatabase()
        config_table_name = "coin_portfolio_config"
        if config_table_name not in database.get_all_tables():
            database.write(
                Query.create_table(
                    config_table_name,
                    {
                        "ticker": "string",
                        "price_reference": "string",
                        "price_reference_config": "json",
                        "sector": "string",
                        "platform": "string",
                        "asset_id": "string",
                        "account": "bytes",
                    },
                )
            )
        self.config = database.read(Query.get_table(config_table_name))

    async def _process_row(self, row: dict) -> None:
        ticker = row["ticker"]
        platform = row["platform"]
        sector = row["sector"]
        coin = Coin.get_coin(
            ticker,
            row["price_reference"],
            row["price_reference_config"],
            sector,
        )
        balance, price = await asyncio.gather(
            coin.get_balance(
                platform, row["asset_id"], self.cipher.decrypt(row["account"])
            ),
            coin.price,
        )
        usd_value = balance * price
        self._total_usd_value += usd_value
        add_to_dict(self._coin_balances, ticker, balance)
        add_to_dict(self._platform_exposure, platform, usd_value)
        add_to_dict(self._sector_exposure, sector, usd_value)

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        self._total_usd_value = Decimal("0")
        self._coin_balances = {}
        self._platform_exposure = {}
        self._sector_exposure = {}
        await asyncio.gather(
            *[self._process_row(row) for row in self.config.get_rows()]
        )
        snapshot = {
            "Coins": [
                await Coin.get_coin_by_ticker(ticker).display_balance(
                    self._coin_balances[ticker]
                )
                for ticker in self._coin_balances
            ]
        }
        return (
            self._total_usd_value,
            snapshot,
            self._platform_exposure,
            self._sector_exposure,
        )
