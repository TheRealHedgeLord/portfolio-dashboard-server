import asyncio

from decimal import Decimal
from datetime import datetime

from utils import add_to_dict
from state.serializers import ColumnType
from dapps.ethena import sUSDe
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker


class EthenaTracker(BaseTracker):
    config_table_name = "ethena_tracker_config"
    config_table_schema = {
        "account": ColumnType.bytes,
    }

    async def _process_row(self, row: dict) -> None:
        account: str = self.cipher.decrypt(row["account"])  # type: ignore
        row_title = f"Ethena {account[0:5]}...{account[-3::]}"
        balance, unlock_time = await self.sUSDe.get_pending_withdrawal(account)
        self._total_usd_value += balance
        usde = Coin.get_coin("USDe", "USD", {}, "StableCoins")
        self._report[row_title] = [
            await usde.display_balance(balance),
            f"Unlock Time: {datetime.fromtimestamp(unlock_time).strftime('%Y-%m-%d %H:%M:%S')}",
        ]

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        self.sUSDe = sUSDe()
        self._total_usd_value = Decimal("0")
        self._report: dict[str, list] = {}
        await asyncio.gather(
            *[self._process_row(row) for row in self.config.get_rows()]
        )
        return (
            self._total_usd_value,
            self._report,
            {"Ethereum": self._total_usd_value},
            {"StableCoins": self._total_usd_value},
        )
