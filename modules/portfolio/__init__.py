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
from modules.portfolio.trackers.aave_tracker import AaveTracker
from modules.portfolio.trackers.gmx_tracker import GMXTracker
from modules.portfolio.trackers.nft_tracker import NFTTracker
from modules.portfolio.trackers.conic_tracker import ConicTracker
from modules.portfolio.trackers.sky_tracker import SkyTracker
from modules.portfolio.trackers.ethena_tracker import EthenaTracker
from modules.portfolio.trackers.benddao_ape_staking_tracker import (
    BendDaoApeStakingTracker,
)
from modules.portfolio.trackers.pendle_tracker import PendleTracker
from web2.coingecko import CoinGecko
from web2.telegram import TelegramBot
from visualization import Canvas
from visualization.color import get_pie_chart_color


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


class PortfolioModule:
    trackers = [
        CoinTracker,
        CompoundTracker,
        AaveTracker,
        GMXTracker,
        NFTTracker,
        ConicTracker,
        SkyTracker,
        BendDaoApeStakingTracker,
        PendleTracker,
        EthenaTracker,
    ]
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
            coingecko = CoinGecko(os.environ["COINGECKO_API_KEY"])
            btc, eth, sol = await coingecko.get_token_data(
                "bitcoin", "ethereum", "solana"
            )
            market_prices = {"BTC": btc, "ETH": eth, "SOL": sol}
            trackers = [tracker(self.state, passphrase) for tracker in self.trackers]
            await asyncio.gather(*[tracker.initialize() for tracker in trackers])
            all_modules_snapshots = await asyncio.gather(
                *[
                    tracker.get_snapshot()
                    for tracker in trackers
                    if tracker.config.row_count > 0
                ]
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

    async def get_snapshot(self, index: str = "0") -> None:
        i = int(index)
        table = await self.state.read(
            Query(
                f"SELECT * FROM {self.snapshot_table_name} ORDER BY timestamp DESC LIMIT {i+1}"
            )
        )
        timestamp = table.get_column("timestamp")[i]
        total_usd_value = table.get_column("total_usd_value")[i]
        market_prices = table.get_column("market_prices")[i]
        report = table.get_column("report")[i]
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

    async def visualize_portfolio(self) -> None:
        table = await self.state.read(
            Query.get_table(
                self.snapshot_table_name,
                columns=[
                    "timestamp",
                    "total_usd_value",
                    "platform_exposure",
                    "sector_exposure",
                ],
            )
        )
        timestamp: list[int] = table.get_column("timestamp")  # type: ignore
        total_usd_value: list[Decimal] = table.get_column("total_usd_value")  # type: ignore
        platform_exposure: list[dict[str, float]] = table.get_column("platform_exposure")  # type: ignore
        sector_exposure: list[dict[str, float]] = table.get_column("sector_exposure")  # type: ignore
        usd_value_data = [["timestamp", "USD Value"]] + [
            [
                datetime.fromtimestamp(timestamp[i]).strftime(DATETIME_FORMAT),
                float(total_usd_value[i]),
            ]
            for i in range(table.row_count)
        ]
        performance_data = [["timestamp", "PnL"]] + [
            [
                datetime.fromtimestamp(timestamp[i]).strftime(DATETIME_FORMAT),
                float(total_usd_value[i] / total_usd_value[0] - Decimal(1)) * 100,
            ]
            for i in range(table.row_count)
        ]
        sector_heads = []
        for row in sector_exposure:
            for key in row:
                if key not in sector_heads:
                    sector_heads.append(key)
        sector_latest = sector_exposure[-1]
        sector_pie_data = [
            ["Sector", "Exposure"],
            *[
                [key, sector_latest[key]]
                for key in sorted(
                    sector_latest, key=lambda x: sector_latest[x], reverse=True
                )
            ],
        ]
        platform_heads = []
        for row in platform_exposure:
            for key in row:
                if key not in platform_heads:
                    platform_heads.append(key)
        platform_latest = platform_exposure[-1]
        platform_pie_data = [
            ["Platform", "Exposure"],
            *[
                [key, platform_latest[key]]
                for key in sorted(
                    platform_latest, key=lambda x: platform_latest[x], reverse=True
                )
            ],
        ]
        canvas = Canvas()
        canvas.add_chart(
            "AreaChart",
            "Portfolio Value",
            usd_value_data,
            options={
                "vAxis": {
                    "viewWindow": {"min": int(min(total_usd_value) / 1000000) * 1000000}
                }
            },
        )
        canvas.add_chart(
            "AreaChart",
            "Portfolio Performance",
            performance_data,
            options={"vAxis": {"format": "#'%'"}},
        )
        canvas.add_chart(
            "PieChart",
            "Sector Exposure",
            sector_pie_data,
            options=get_pie_chart_color(sector_pie_data),
        )
        canvas.add_chart(
            "PieChart",
            "Platform Exposure",
            platform_pie_data,
            options=get_pie_chart_color(platform_pie_data),
        )
        canvas.draw()
