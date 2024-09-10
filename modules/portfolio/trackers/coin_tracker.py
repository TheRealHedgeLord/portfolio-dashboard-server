import asyncio

from decimal import Decimal

from state.serializers import ColumnType
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker
from utils import add_to_dict


class CoinTracker(BaseTracker):
    config_table_name = "coin_tracker_config"
    config_table_schema = {
        "ticker": ColumnType.string,
        "price_reference": ColumnType.string,
        "price_reference_config": ColumnType.json,
        "sector": ColumnType.string,
        "platform": ColumnType.string,
        "asset_id": ColumnType.string,
        "account": ColumnType.bytes,
    }

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
