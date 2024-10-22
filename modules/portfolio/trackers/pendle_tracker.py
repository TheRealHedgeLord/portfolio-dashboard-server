import time
import asyncio

from decimal import Decimal

from state.serializers import ColumnType
from dapps.pendle import get_market
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker
from utils import add_to_dict


class PendleTracker(BaseTracker):
    config_table_name = "pendle_tracker_config"
    config_table_schema = {
        "chain": ColumnType.string,
        "market_address": ColumnType.string,
        "price_reference": ColumnType.string,
        "price_reference_config": ColumnType.json,
        "sector": ColumnType.string,
        "account": ColumnType.bytes,
    }

    async def _process_row(self, row: dict) -> None:
        market = await get_market(row["chain"], row["market_address"])
        pt_market_value = await market.get_pt_market_value(
            self.cipher.decrypt(row["account"])  # type: ignore
        )
        pt = Coin.get_coin(
            "PT", row["price_reference"], row["price_reference_config"], row["sector"]
        )
        usd_value = (await pt.price) * pt_market_value
        days_to_maturity = int((market.expiry - time.time()) / (24 * 60 * 60))
        self._snapshot["Pendle"].append(
            [
                market.name,
                await pt.display_balance(pt_market_value),
                f"Time To Maturity: {days_to_maturity} days",
            ]
        )
        self._total_usd_value += usd_value
        add_to_dict(self._platform_exposure, row["chain"], usd_value)
        add_to_dict(self._sector_exposure, row["sector"], usd_value)

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        self._total_usd_value = Decimal("0")
        self._snapshot = {"Pendle": []}
        self._platform_exposure = {}
        self._sector_exposure = {}
        await asyncio.gather(
            *[self._process_row(row) for row in self.config.get_rows()]
        )
        return (
            self._total_usd_value,
            self._snapshot,
            self._platform_exposure,
            self._sector_exposure,
        )
