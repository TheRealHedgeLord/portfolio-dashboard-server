import asyncio

from decimal import Decimal

from state.serializers import ColumnType
from dapps.conic import ConicDebtPool
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker
from modules.portfolio.display import (
    display_decimal,
    display_stable_coins,
    display_asset,
)


class ConicTracker(BaseTracker):
    config_table_name = "conic_tracker_config"
    config_table_schema = {"account": ColumnType.bytes}

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        conic = ConicDebtPool()
        best_exits = await asyncio.gather(
            *[
                conic.get_best_exit(self.cipher.decrypt(account))  # type: ignore
                for account in self.config.get_column("account")
            ]
        )
        total_usd_value = sum(
            [best_exit["total_usd_value"] for best_exit in best_exits]
        )
        swap_amount = sum([best_exit["swap_amount"] for best_exit in best_exits])
        redeem_amount = sum([best_exit["redeem_amount"] for best_exit in best_exits])
        crvusd = sum([best_exit["crvusd_amount_out"] for best_exit in best_exits])
        crv_price = best_exits[0]["redeemed_tokens"]["crv"]["price"]
        cvx_price = best_exits[0]["redeemed_tokens"]["cvx"]["price"]
        cnc_price = best_exits[0]["redeemed_tokens"]["cnc"]["price"]
        crv = sum(
            [best_exit["redeemed_tokens"]["crv"]["amount"] for best_exit in best_exits]
        )
        cvx = sum(
            [best_exit["redeemed_tokens"]["cvx"]["amount"] for best_exit in best_exits]
        )
        cnc = sum(
            [best_exit["redeemed_tokens"]["cnc"]["amount"] for best_exit in best_exits]
        )
        report = {
            "ConicFinance": [
                [
                    "Debt Pool",
                    f"Swap Amount: {display_decimal(swap_amount)}",  # type: ignore
                    f"Redeem Amount: {display_decimal(redeem_amount)}",  # type: ignore
                    display_stable_coins("crvUSD", crvusd),  # type: ignore
                    display_asset("CRV", crv, crv_price, crv * crv_price),  # type: ignore
                    display_asset("CVX", cvx, cvx_price, cvx * cvx_price),  # type: ignore
                    display_asset("CNC", cnc, cnc_price, cnc * cnc_price),  # type: ignore
                ]
            ]
        }
        platform_exposure = {"Ethereum": total_usd_value}
        sector_exposure = {"Others": total_usd_value}
        return total_usd_value, report, platform_exposure, sector_exposure  # type: ignore
