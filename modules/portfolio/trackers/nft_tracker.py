import asyncio

from decimal import Decimal

from state.serializers import ColumnType
from modules.portfolio.trackers.base_tracker import BaseTracker
from modules.portfolio.assets import NFT
from utils import add_to_dict


class NFTTracker(BaseTracker):
    config_table_name = "nft_tracker_config"
    config_table_schema = {
        "ticker": ColumnType.string,
        "price_reference": ColumnType.string,
        "price_reference_config": ColumnType.json,
        "base_currency": ColumnType.string,
        "platform": ColumnType.string,
        "asset_id": ColumnType.string,
        "account": ColumnType.bytes,
    }

    async def _process_row(self, row: dict) -> None:
        ticker = row["ticker"]
        platform = row["platform"]
        base_currency = row["base_currency"]
        nft = NFT.get_nft(
            ticker, row["price_reference"], row["price_reference_config"], base_currency
        )
        balance, floor_price_in_usd = await asyncio.gather(
            nft.get_balance(
                platform, row["asset_id"], self.cipher.decrypt(row["account"])
            ),
            nft.floor_price_in_usd,
        )
        usd_value = balance * floor_price_in_usd
        self._total_usd_value += usd_value
        add_to_dict(self._nft_balances, ticker, balance)
        add_to_dict(self._platform_exposure, platform, usd_value)

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        self._total_usd_value = Decimal("0")
        self._nft_balances = {}
        self._platform_exposure = {}
        await asyncio.gather(
            *[self._process_row(row) for row in self.config.get_rows()]
        )
        snapshot = {
            "NFTs": [
                await NFT.get_nft_by_ticker(ticker).display_balance(
                    self._nft_balances[ticker]
                )
                for ticker in self._nft_balances
            ]
        }
        return (
            self._total_usd_value,
            snapshot,
            self._platform_exposure,
            {"NFT": self._total_usd_value},
        )
