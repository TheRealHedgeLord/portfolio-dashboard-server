import os
import time
import asyncio

from decimal import Decimal
from datetime import datetime

from state import RDS
from state.sql import Query
from state.serializers import ColumnType, serialize
from evm import EVM
from dapps.gmx.gm import SupportedMarkets
from dapps.gmx.glv import SupportedGLV
from modules.gmx.index import create_index
from modules.gmx.optimizer import OptimizedGMX
from modules.gmx.constants import ALL_TRACKED_CHAINS, ALL_TRACKED_GM, ALL_TRACKED_GLV
from web2.coingecko import CoinGecko
from visualization import Canvas


class GMXPerformanceTracker:
    table_name = "gmx_performance_tracker"
    table_schema = {
        "timestamp": ColumnType.integer,
        "chain": ColumnType.string,
        "asset": ColumnType.string,
        "asset_amount": ColumnType.decimal,
        "long_token_withdraw_amount": ColumnType.decimal,
        "short_token_withdraw_amount": ColumnType.decimal,
    }

    def __init__(self, state: RDS) -> None:
        self.state = state
        self.coingecko = CoinGecko(os.environ["COINGECKO_API_KEY"])

    async def initialize_table(self) -> None:
        all_tables = await self.state.get_all_tables()
        if self.table_name not in all_tables:
            await self.state.write(
                Query.create_table(self.table_name, self.table_schema)
            )

    async def _track_gm(
        self, chain: str, gm: SupportedMarkets, asset_amount: Decimal, timestamp: int
    ) -> None:
        gmx = OptimizedGMX(EVM.get_chain(chain))
        long_token_withdraw_amount, short_token_withdraw_amount = (
            await gmx.get_gm_withdraw_amount_out(asset_amount, gm)
        )
        row = {
            "timestamp": timestamp,
            "chain": chain,
            "asset": gm,
            "asset_amount": asset_amount,
            "long_token_withdraw_amount": long_token_withdraw_amount,
            "short_token_withdraw_amount": short_token_withdraw_amount,
        }
        await self.state.write(Query.insert_row(self.table_name, row))

    async def _track_glv(
        self, chain: str, glv: SupportedGLV, asset_amount: Decimal, timestamp: int
    ) -> None:
        gmx = OptimizedGMX(EVM.get_chain(chain))
        long_token_withdraw_amount, short_token_withdraw_amount = (
            await gmx.get_glv_withdraw_amount_out(asset_amount, glv)
        )
        row = {
            "timestamp": timestamp,
            "chain": chain,
            "asset": glv,
            "asset_amount": asset_amount,
            "long_token_withdraw_amount": long_token_withdraw_amount,
            "short_token_withdraw_amount": short_token_withdraw_amount,
        }
        await self.state.write(Query.insert_row(self.table_name, row))

    async def track_performance(self, asset_amount: str) -> None:
        timestamp = int(time.time())
        (btc, _), (eth, _), (sol, _), (link, _) = await self.coingecko.get_token_data(
            "bitcoin", "ethereum", "solana", "chainlink"
        )
        await self.state.write(
            Query.insert_rows(
                self.table_name,
                [key for key in self.table_schema],
                [
                    [timestamp, "N/A", "BTC", Decimal(1), Decimal(0), btc],
                    [timestamp, "N/A", "ETH", Decimal(1), Decimal(0), eth],
                    [timestamp, "N/A", "SOL", Decimal(1), Decimal(0), sol],
                    [timestamp, "N/A", "LINK", Decimal(1), Decimal(0), link],
                ],
            )
        )
        gm_tasks = []
        for chain in ALL_TRACKED_CHAINS:
            gm_tasks += [
                self._track_gm(chain, gm, Decimal(asset_amount), timestamp)
                for gm in ALL_TRACKED_GM[chain]
            ]
        await asyncio.gather(*gm_tasks)
        glv_tasks = []
        for chain in ALL_TRACKED_GLV:
            glv_tasks += [
                self._track_glv(chain, glv, Decimal(asset_amount), timestamp)
                for glv in ALL_TRACKED_GLV[chain]
            ]
        await asyncio.gather(*glv_tasks)

    async def get_asset_performance(self, chain: str, asset: str) -> None:
        table = await self.state.read(
            Query.get_table(
                self.table_name,
                match_values={"chain": chain, "asset": asset},
                order_by="timestamp",
            )
        )
        print(table)

    async def _plot_dual_exposure_asset(
        self, canvas: Canvas, chain: str, asset: str, principal: str, weight: str
    ) -> None:
        table = await self.state.read(
            Query(
                """
                SELECT
                    gm.timestamp,
                    gm.asset_amount,
                    gm.long_token_withdraw_amount AS principal_amount,
                    gm.short_token_withdraw_amount AS usd_amount,
                    principal.short_token_withdraw_amount AS price
                FROM
                    gmx_performance_tracker gm
                JOIN
                    gmx_performance_tracker principal
                ON
                    gm.timestamp = principal.timestamp
                WHERE
                    gm.chain = {chain}
                AND
                    gm.asset = {gm_asset}
                AND
                    principal.asset = {principal_asset}
                ORDER BY gm.timestamp ASC
                """.format(
                    chain=serialize(chain),
                    gm_asset=serialize(asset),
                    principal_asset=serialize(principal),
                )
            )
        )
        asset_usd_value = [
            (
                table.get_column("principal_amount")[i] * table.get_column("price")[i]  # type: ignore
                + table.get_column("usd_amount")[i]
            )
            / table.get_column("asset_amount")[i]
            for i in range(table.row_count)
        ]
        asset_performance = [value / asset_usd_value[0] for value in asset_usd_value]  # type: ignore
        index_performance = create_index(Decimal(weight), table.get_column("price"))  # type: ignore
        data = [
            ["timestamp", "Asset Performance", "Index Performance"],
            *[
                [
                    datetime.fromtimestamp(table.get_column("timestamp")[i]).strftime(  # type: ignore
                        "%Y-%m-%d %H:%M"
                    ),
                    float(asset_performance[i]),
                    float(index_performance[i]),
                ]
                for i in range(table.row_count)
            ],
        ]
        timestamp_diff = (
            table.get_column("timestamp")[-1] - table.get_column("timestamp")[0]
        )  # type: ignore
        apy = round(
            (float(asset_performance[-1] / index_performance[-1]) - 1)  # type: ignore
            * (365 * 24 * 60 * 60 / timestamp_diff)
            * 100,
            2,
        )
        days = days = int(timestamp_diff / (24 * 60 * 60))
        canvas.add_chart(
            "AreaChart",
            f"{asset} (outperformance over index {days} days prorated APY {apy}%)",
            data,
        )

    async def _plot_single_exposure_asset(
        self, canvas: Canvas, chain: str, asset: str
    ) -> None:
        table = await self.state.read(
            Query.get_table(
                self.table_name,
                columns=[
                    "timestamp",
                    "asset_amount",
                    "long_token_withdraw_amount",
                    "short_token_withdraw_amount",
                ],
                match_values={"chain": chain, "asset": asset},
                order_by="timestamp",
            )
        )
        timestamp: list[int] = table.get_column("timestamp")  # type: ignore
        asset_amount: list[Decimal] = table.get_column("asset_amount")  # type: ignore
        long_token_withdraw_amount: list[Decimal] = table.get_column(
            "long_token_withdraw_amount"
        )  # type: ignore
        short_token_withdraw_amount: list[Decimal] = table.get_column(
            "short_token_withdraw_amount"
        )  # type: ignore
        first = (
            long_token_withdraw_amount[0] + short_token_withdraw_amount[0]
        ) / asset_amount[0]
        last = (
            long_token_withdraw_amount[-1] + short_token_withdraw_amount[-1]
        ) / asset_amount[-1]
        apy = round(
            float((last - first) / first)
            * (365 * 24 * 60 * 60 / (timestamp[-1] - timestamp[0]))
            * 100,
            2,
        )
        days = int((timestamp[-1] - timestamp[0]) / (24 * 60 * 60))
        underlying = asset.split("-")[-1]
        data = [
            ["timestamp", f"{underlying} / {asset}"],
            *[
                [
                    datetime.fromtimestamp(timestamp[i]).strftime("%Y-%m-%d %H:%M"),
                    float(
                        (long_token_withdraw_amount[i] + short_token_withdraw_amount[i])
                        / asset_amount[i]
                    ),
                ]
                for i in range(table.row_count)
            ],
        ]
        canvas.add_chart(
            "AreaChart", f"{asset} porformance ({days} days prorated APY {apy}%)", data
        )

    async def plot_single_exposure_asset(self, chain: str, *assets: str) -> None:
        canvas = Canvas()
        await asyncio.gather(
            *[
                self._plot_single_exposure_asset(canvas, chain, asset)
                for asset in assets
            ]
        )
        canvas.draw()

    async def plot_dual_exposure_asset(self, chain: str, *assets: str) -> None:
        canvas = Canvas()
        await asyncio.gather(
            *[
                self._plot_dual_exposure_asset(canvas, chain, *asset.split(":"))
                for asset in assets
            ]
        )
        canvas.draw()
