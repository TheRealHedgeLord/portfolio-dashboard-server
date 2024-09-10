import asyncio

from decimal import Decimal

from utils import add_to_dict
from state.serializers import ColumnType
from dapps.compound import Compound
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker


class CompoundTracker(BaseTracker):
    config_table_name = "compound_tracker_config"
    config_table_schema = {
        "chain": ColumnType.string,
        "fork": ColumnType.string,
        "account": ColumnType.bytes,
        "markets": ColumnType.json,
        "token_sector": ColumnType.string,
        "token_price_reference": ColumnType.string,
        "token_price_reference_config": ColumnType.json,
    }

    async def _process_market(
        self, fork: Compound, ticker: str, market_spec: dict, account: str
    ) -> tuple[str | None, str | None, Decimal, Decimal]:
        ctoken_address = market_spec["ctoken_address"]
        price_reference = market_spec["price_reference"]
        price_reference_config = market_spec["price_reference_config"]
        sector = market_spec["sector"]
        underlying_coin = Coin.get_coin(
            ticker, price_reference, price_reference_config, sector
        )
        price, (supply, debt), collateral_factor = await asyncio.gather(
            underlying_coin.price,
            fork.get_supply_and_borrow_balance(ctoken_address, account),
            fork.get_collateral_factor(ctoken_address),
        )
        adjusted_supply = await underlying_coin.get_adjusted_balance(supply)
        adjusted_debt = await underlying_coin.get_adjusted_balance(debt)
        usd_value = (adjusted_supply - adjusted_debt) * price
        self._total_usd_value += usd_value
        add_to_dict(self._platform_exposure, fork.chain.name, usd_value)
        add_to_dict(self._sector_exposure, sector, usd_value)
        supply_report = (
            await underlying_coin.display_balance(adjusted_supply)
            if adjusted_supply > Decimal("0")
            else None
        )
        debt_report = (
            await underlying_coin.display_balance(adjusted_debt)
            if adjusted_debt > Decimal("0")
            else None
        )
        borrowing_power = adjusted_supply * price * collateral_factor
        borrowing_power_used = adjusted_debt * price
        return supply_report, debt_report, borrowing_power, borrowing_power_used

    async def _process_row(self, row: dict) -> None:
        fork = await Compound.get_fork(row["chain"], row["fork"])
        account: str = self.cipher.decrypt(row["account"])  # type: ignore
        row_title = f"{fork.fork} ({fork.chain.name}) {account[0:5]}...{account[-3::]}"
        self._report[row_title] = []
        total_borrowing_power = Decimal("0")
        total_borrowing_power_used = Decimal("0")
        supply_reports = []
        debt_reports = []
        market_snapshots = await asyncio.gather(
            *[
                self._process_market(fork, ticker, row["markets"][ticker], account)
                for ticker in row["markets"]
            ]
        )
        for (
            supply_report,
            debt_report,
            borrowing_power,
            borrowing_power_used,
        ) in market_snapshots:
            if supply_report:
                supply_reports.append(supply_report)
            if debt_report:
                debt_reports.append(debt_report)
            total_borrowing_power += borrowing_power
            total_borrowing_power_used += borrowing_power_used
        if len(supply_reports) > 0:
            self._report[row_title].append(["Supplied"] + supply_reports)
        if len(debt_reports) > 0:
            self._report[row_title].append(["Borrowed"] + debt_reports)
        health_score = (
            round(total_borrowing_power / total_borrowing_power_used, 2)
            if total_borrowing_power_used > Decimal("0")
            else "inf"
        )
        self._report[row_title].append(f"Health Score: {health_score}")
        reward_token = Coin.get_coin(
            fork.token.symbol,
            row["token_price_reference"],
            row["token_price_reference_config"],
            row["token_sector"],
        )
        claimable_reward, reward_token_price = await asyncio.gather(
            fork.get_claimable_rewards(account), reward_token.price
        )
        adjusted_claimable_reward = await reward_token.get_adjusted_balance(
            claimable_reward
        )
        reward_usd_value = adjusted_claimable_reward * reward_token_price
        reward_report = await reward_token.display_balance(adjusted_claimable_reward)
        self._total_usd_value += reward_usd_value
        add_to_dict(self._platform_exposure, fork.chain.name, reward_usd_value)
        add_to_dict(self._sector_exposure, row["token_sector"], reward_usd_value)
        self._report[row_title].append(f"Claimable {reward_report}")

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        self._total_usd_value = Decimal("0")
        self._report: dict[str, list] = {}
        self._platform_exposure = {}
        self._sector_exposure = {}
        await asyncio.gather(
            *[self._process_row(row) for row in self.config.get_rows()]
        )
        return (
            self._total_usd_value,
            self._report,
            self._platform_exposure,
            self._sector_exposure,
        )
