import asyncio

from decimal import Decimal

from state import RDS
from state.serializers import ColumnType
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker
from dapps.gmx import GMX
from dapps.gmx.gm import SupportedMarkets
from evm import EVM
from utils import add_to_dict, dict_add


class GMXTracker(BaseTracker):
    config_table_name = "gmx_tracker_config"
    config_table_schema = {
        "chain": ColumnType.string,
        "markets": ColumnType.json,
        "account": ColumnType.bytes,
    }

    def __init__(self, state: RDS, passphrase: str) -> None:
        super().__init__(state, passphrase)
        self.gmx = Coin.get_coin("GMX", "CoinGecko", {"token_id": "gmx"}, "GMX")
        self.eth = Coin.get_coin("ETH", "ETH", {}, "ETH")

    async def _process_market(
        self, gmx_app: GMX, market: SupportedMarkets, market_spec: dict, account: str
    ) -> None:
        long_token_amount, short_token_amount = (
            await gmx_app.get_gm_withdraw_amount_out_for_account(account, market)
        )
        long_token = Coin.get_coin(**market_spec["long_token"])
        short_token = Coin.get_coin(**market_spec["short_token"])
        adjusted_long_token_amount = await long_token.get_adjusted_balance(
            long_token_amount
        )
        adjusted_short_token_amount = await short_token.get_adjusted_balance(
            short_token_amount
        )
        long_token_usd_value = adjusted_long_token_amount * (await long_token.price)
        short_token_usd_value = adjusted_short_token_amount * (await short_token.price)
        self._total_usd_value += long_token_usd_value + short_token_usd_value
        add_to_dict(
            self._platform_exposure,
            gmx_app.chain.name,
            long_token_usd_value + short_token_usd_value,
        )
        add_to_dict(
            self._sector_exposure,
            market_spec["long_token"]["sector"],
            long_token_usd_value,
        )
        add_to_dict(
            self._sector_exposure,
            market_spec["short_token"]["sector"],
            short_token_usd_value,
        )
        if long_token == short_token:
            self._report["GMX"].append(
                [
                    f"{market} ({gmx_app.chain.name})",
                    await long_token.display_balance(
                        adjusted_long_token_amount + adjusted_short_token_amount
                    ),
                ]
            )
        else:
            self._report["GMX"].append(
                [
                    f"{market} ({gmx_app.chain.name})",
                    await long_token.display_balance(adjusted_long_token_amount),
                    await short_token.display_balance(adjusted_short_token_amount),
                ]
            )

    async def _process_row(self, row: dict) -> None:
        account: str = self.cipher.decrypt(row["account"])  # type: ignore
        chain = EVM.get_chain(row["chain"])
        gmx_app = GMX(chain)
        await asyncio.gather(
            *[
                self._process_market(gmx_app, market, row["markets"][market], account)
                for market in row["markets"]
            ]
        )
        staked_gmx, reward_gmx = await gmx_app.get_gmx_staking(account)
        dict_add(
            self._staking,  # type: ignore
            {
                "staked_gmx": staked_gmx,
                "reward_gmx": reward_gmx,
            },
        )
        gmx_usd_value = (staked_gmx + reward_gmx) * (await self.gmx.price)
        usd_value = gmx_usd_value
        self._total_usd_value += usd_value
        add_to_dict(self._platform_exposure, chain.name, usd_value)
        dict_add(self._sector_exposure, {"GMX": gmx_usd_value})

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        self._total_usd_value = Decimal("0")
        self._report: dict[str, list] = {"GMX": []}
        self._platform_exposure = {}
        self._sector_exposure = {}
        self._staking = {
            "staked_gmx": Decimal("0"),
            "reward_gmx": Decimal("0"),
            "reward_eth": Decimal("0"),
        }
        await asyncio.gather(
            *[self._process_row(row) for row in self.config.get_rows()]
        )
        self._report["GMX"] += [
            "Staked " + (await self.gmx.display_balance(self._staking["staked_gmx"])),
            "Reward " + (await self.gmx.display_balance(self._staking["reward_gmx"])),
        ]
        return (
            self._total_usd_value,
            self._report,
            self._platform_exposure,
            self._sector_exposure,
        )
