import asyncio

from decimal import Decimal

from state import RDS
from state.serializers import ColumnType
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker
from modules.portfolio.display import display_stable_coins, display_asset
from dapps.sky import Sky


class SkyTracker(BaseTracker):
    config_table_name = "sky_tracker_config"
    config_table_schema = {
        "account": ColumnType.bytes,
    }

    def __init__(self, state: RDS, passphrase: str) -> None:
        super().__init__(state, passphrase)
        self.sky = Sky()

    async def get_all_staked_usds(self) -> Decimal:
        usds = await asyncio.gather(
            *[
                self.sky.get_staked_usds(self.cipher.decrypt(account))  # type: ignore
                for account in self.config.get_column("account")
            ]
        )
        return sum(usds)  # type: ignore

    async def get_all_sky_reward(self) -> Decimal:
        sky = await asyncio.gather(
            *[
                self.sky.get_sky_reward(self.cipher.decrypt(account))  # type: ignore
                for account in self.config.get_column("account")
            ]
        )
        return sum(sky)  # type: ignore

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        usds, sky, price = await asyncio.gather(
            self.get_all_staked_usds(),
            self.get_all_sky_reward(),
            self.sky.sky_price_from_mkr(),
        )
        total_usd_value = usds + sky * price
        snapshot = {
            "Sky": [
                display_stable_coins("USDS", usds),
                display_asset("SKY", sky, price, sky * price),
            ]
        }
        platform_exposure = {"Ethereum": total_usd_value}
        sector_exposure = {"StableCoins": usds, "Others": sky * price}
        return total_usd_value, snapshot, platform_exposure, sector_exposure
