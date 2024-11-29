import asyncio

from decimal import Decimal

from utils import add_to_dict
from state.serializers import ColumnType
from dapps.aave import AAVE
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker


class AaveTracker(BaseTracker):
    config_table_name = "aave_tracker_config"
    config_table_schema = {
        "chain": ColumnType.string,
        "fork": ColumnType.string,
        "a_tokens": ColumnType.json,
        "debt_tokens": ColumnType.json,
        "account": ColumnType.bytes,
    }

    async def _process_a_token(
        self,
        row_title: str,
        fork: AAVE,
        ticker: str,
        a_token_address: str,
        account: str,
        price_reference: str,
        price_reference_config: dict,
        sector: str,
    ) -> Decimal:
        liquidation_threshold, balance = await asyncio.gather(
            fork.get_liquidation_threshold_for_a_token(a_token_address),
            fork.get_supply_or_debt_amount(a_token_address, account),
        )
        coin = Coin.get_coin(ticker, price_reference, price_reference_config, sector)
        adjusted_balance = await coin.get_adjusted_balance(balance)
        price = await coin.price
        usd_value = adjusted_balance * price
        self._total_usd_value += usd_value
        add_to_dict(self._platform_exposure, fork.chain.name, usd_value)
        add_to_dict(self._sector_exposure, sector, usd_value)
        self._report[row_title][0].append(await coin.display_balance(adjusted_balance))
        return liquidation_threshold * usd_value

    async def _process_debt(
        self,
        row_title: str,
        fork: AAVE,
        ticker: str,
        debt_token_address: str,
        account: str,
        price_reference: str,
        price_reference_config: dict,
        sector: str,
    ) -> Decimal:
        balance = await fork.get_supply_or_debt_amount(debt_token_address, account)
        coin = Coin.get_coin(ticker, price_reference, price_reference_config, sector)
        adjusted_balance = await coin.get_adjusted_balance(balance)
        price = await coin.price
        usd_value = adjusted_balance * price
        self._total_usd_value -= usd_value
        add_to_dict(self._platform_exposure, fork.chain.name, -usd_value)
        add_to_dict(self._sector_exposure, sector, -usd_value)
        self._report[row_title][1].append(await coin.display_balance(adjusted_balance))
        return usd_value

    async def _process_row(self, row: dict) -> None:
        account: str = self.cipher.decrypt(row["account"])  # type: ignore
        fork = AAVE(row["fork"], row["chain"])
        row_title = f"{fork.fork} ({fork.chain.name}) {account[0:5]}...{account[-3::]}"
        self._report[row_title] = [["Supplied"]]
        supply = await asyncio.gather(
            *[
                self._process_a_token(
                    row_title,
                    fork,
                    ticker,
                    row["a_tokens"][ticker]["address"],
                    account,
                    row["a_tokens"][ticker]["price_reference"],
                    row["a_tokens"][ticker]["price_reference_config"],
                    row["a_tokens"][ticker]["sector"],
                )
                for ticker in row["a_tokens"]
            ]
        )
        collateral_value = sum(supply)
        if len(row["debt_tokens"]) > 0:
            self._report[row_title].append(["Borrowed"])
            debt = await asyncio.gather(
                *[
                    self._process_debt(
                        row_title,
                        fork,
                        ticker,
                        row["debt_tokens"][ticker]["address"],
                        account,
                        row["debt_tokens"][ticker]["price_reference"],
                        row["debt_tokens"][ticker]["price_reference_config"],
                        row["debt_tokens"][ticker]["sector"],
                    )
                    for ticker in row["debt_tokens"]
                ]
            )
            debt_value = sum(debt)
        else:
            debt_value = Decimal("0")
        if debt_value > Decimal("0"):
            health = round(collateral_value / debt_value, 2)
        else:
            health = "inf"
        self._report[row_title].append(f"Health Score: {health}")

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
