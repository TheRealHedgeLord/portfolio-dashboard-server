import os
import time
import uuid
import traceback
import asyncio

from decimal import Decimal
from datetime import datetime
from typing import Literal

from utils import dict_add, to_json
from state import RDS
from state.sql import Query
from state.serializers import ColumnType
from modules.portfolio.display import print_snapshot_report
from modules.portfolio.context import btc_price, eth_price, sol_price
from modules.portfolio.trackers.coin_tracker import CoinTracker
from modules.portfolio.trackers.compound_tracker import CompoundTracker
from modules.portfolio.trackers.gmx_tracker import GMXTracker
from modules.portfolio.trackers.nft_tracker import NFTTracker
from modules.portfolio.trackers.conic_tracker import ConicTracker
from web2.telegram import TelegramBot
from visualization import Chart


class PortfolioModule:
    trackers = [CoinTracker, CompoundTracker, GMXTracker, NFTTracker, ConicTracker]
    snapshot_table_name = "portfolio_snapshots"
    snapshot_table_schema = {
        "timestamp": ColumnType.integer,
        "market_prices": ColumnType.json,
        "total_usd_value": ColumnType.decimal,
        "report": ColumnType.json,
        "platform_exposure": ColumnType.json,
        "sector_exposure": ColumnType.json,
    }
    logs_table_name = "portfolio_logs"
    logs_table_schema = {
        "timestamp": ColumnType.integer,
        "error_id": ColumnType.string,
        "stack_trace": ColumnType.string,
    }

    def __init__(self, state: RDS) -> None:
        self.state = state

    async def take_snapshot(self, passphrase: str) -> None:
        try:
            timestamp = int(time.time())
            btc, eth, sol = await asyncio.gather(btc_price(), eth_price(), sol_price())
            market_prices = {"BTC": btc, "ETH": eth, "SOL": sol}
            trackers = [tracker(self.state, passphrase) for tracker in self.trackers]
            await asyncio.gather(*[tracker.initialize() for tracker in trackers])
            all_modules_snapshots = await asyncio.gather(
                *[tracker.get_snapshot() for tracker in trackers]
            )
            total_usd_value = Decimal("0")
            report = {}
            platform_exposure = {}
            sector_exposure = {}
            for (
                module_usd_value,
                module_report,
                module_platform_exposure,
                module_sector_exposure,
            ) in all_modules_snapshots:
                total_usd_value += module_usd_value
                report.update(module_report)
                dict_add(platform_exposure, module_platform_exposure)
                dict_add(sector_exposure, module_sector_exposure)
            await self.state.write(
                Query.insert_row(
                    self.snapshot_table_name,
                    {
                        "timestamp": timestamp,
                        "market_prices": to_json(market_prices),
                        "total_usd_value": total_usd_value,
                        "report": report,
                        "platform_exposure": to_json(platform_exposure),
                        "sector_exposure": to_json(sector_exposure),
                    },
                )
            )
        except:
            timestamp = int(time.time())
            stack_trace = traceback.format_exc()
            error_id = uuid.uuid4().hex
            await self.state.write(
                Query.insert_row(
                    self.logs_table_name,
                    {
                        "timestamp": timestamp,
                        "error_id": error_id,
                        "stack_trace": stack_trace,
                    },
                )
            )
            telegram = TelegramBot(os.environ["TELEGRAM_BOT_TOKEN"])
            await telegram.send_message(
                os.environ["SERVER_LOG_CHAT_ID"],
                f"Error happend when taking snapshot, id: {error_id}",
            )

    async def get_snapshot(self, index: str = "-1") -> None:
        table = await self.state.read(Query.get_table(self.snapshot_table_name))
        timestamp = table.get_column("timestamp")[int(index)]
        total_usd_value = table.get_column("total_usd_value")[int(index)]
        market_prices = table.get_column("market_prices")[int(index)]
        report = table.get_column("report")[int(index)]
        snapshot = print_snapshot_report(timestamp, total_usd_value, market_prices, report)  # type: ignore
        print(snapshot)

    async def initialize_all_tables(self) -> None:
        existing_tables = await self.state.get_all_tables()
        for table_name, table_schema in [
            (self.snapshot_table_name, self.snapshot_table_schema),
            (self.logs_table_name, self.logs_table_schema),
        ] + [
            (tracker.config_table_name, tracker.config_table_schema)
            for tracker in self.trackers
        ]:
            if table_name not in existing_tables:
                await self.state.write(Query.create_table(table_name, table_schema))

    async def plot_portfolio_value(self) -> None:
        table = await self.state.read(Query.get_table(self.snapshot_table_name))
        timestamp: list[int] = table.get_column("timestamp")  # type: ignore
        total_usd_value: list[Decimal] = table.get_column("total_usd_value")  # type: ignore
        data = [["timestamp", "USD Value"]] + [
            [
                datetime.fromtimestamp(timestamp[i]).strftime("%Y-%m-%d %H:%M"),
                float(total_usd_value[i]),
            ]
            for i in range(table.row_count)
        ]
        chart = Chart("AreaChart", "Portfolio USD Value", data)
        chart.draw()

    async def plot_sector_exposure(
        self, chart_type: Literal["pie", "area"] = "pie"
    ) -> None:
        table = await self.state.read(Query.get_table(self.snapshot_table_name))
        sector_exposure: list[dict[str, float]] = table.get_column("sector_exposure")  # type: ignore
        if chart_type == "area":
            timestamp: list[int] = table.get_column("timestamp")  # type: ignore
            total_usd_value: list[Decimal] = table.get_column("total_usd_value")  # type: ignore
            heads = []
            for row in sector_exposure:
                for key in row:
                    if key not in heads:
                        heads.append(key)
            data = [["timestamp"] + heads] + [
                [datetime.fromtimestamp(timestamp[i]).strftime("%Y-%m-%d %H:%M")]
                + [
                    (
                        0
                        if key not in sector_exposure[i]
                        else sector_exposure[i][key] / float(total_usd_value[i])
                    )
                    for key in heads
                ]
                for i in range(table.row_count)
            ]
            chart = Chart(
                "AreaChart", "Sector Exposure", data, options={"is_stacked": True}
            )
        else:
            latest = sector_exposure[-1]
            data = [["Sector", "Exposure"], *[[key, latest[key]] for key in latest]]
            chart = Chart("PieChart", "Sector Exposure", data)
        chart.draw()

    async def plot_platform_exposure(
        self, chart_type: Literal["pie", "area"] = "pie"
    ) -> None:
        table = await self.state.read(Query.get_table(self.snapshot_table_name))
        platform_exposure: list[dict[str, float]] = table.get_column("platform_exposure")  # type: ignore
        if chart_type == "area":
            timestamp: list[int] = table.get_column("timestamp")  # type: ignore
            total_usd_value: list[Decimal] = table.get_column("total_usd_value")  # type: ignore
            heads = []
            for row in platform_exposure:
                for key in row:
                    if key not in heads:
                        heads.append(key)
            data = [["timestamp"] + heads] + [
                [datetime.fromtimestamp(timestamp[i]).strftime("%Y-%m-%d %H:%M")]
                + [
                    (
                        0
                        if key not in platform_exposure[i]
                        else platform_exposure[i][key] / float(total_usd_value[i])
                    )
                    for key in heads
                ]
                for i in range(table.row_count)
            ]
            chart = Chart(
                "AreaChart", "Sector Exposure", data, options={"is_stacked": True}
            )
        else:
            latest = platform_exposure[-1]
            data = [["Platform", "Exposure"], *[[key, latest[key]] for key in latest]]
            chart = Chart("PieChart", "Platform Exposure", data)
        chart.draw()
