import os
import time
import uuid
import traceback
import asyncio

from decimal import Decimal

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
from web2.telegram import TelegramBot


TRACKERS = [CoinTracker, CompoundTracker, GMXTracker, NFTTracker]


PORTFOLIO_SNAPSHOT_TABLE_SCHEMA = {
    "table_name": "portfolio_snapshots",
    "columns_schema": {
        "timestamp": ColumnType.integer,
        "market_prices": ColumnType.json,
        "total_usd_value": ColumnType.decimal,
        "report": ColumnType.json,
        "platform_exposure": ColumnType.json,
        "sector_exposure": ColumnType.json,
    },
}

PORTFOLIO_LOGS_TABLE_SCHEMA = {
    "table_name": "portfolio_logs",
    "columns_schema": {
        "timestamp": ColumnType.integer,
        "error_id": ColumnType.string,
        "stack_trace": ColumnType.string,
    },
}


class PortfolioModule:
    def __init__(self, state: RDS) -> None:
        self.state = state

    async def take_snapshot(self, passphrase: str) -> None:
        try:
            btc, eth, sol = await asyncio.gather(btc_price(), eth_price(), sol_price())
            market_prices = {"BTC": btc, "ETH": eth, "SOL": sol}
            trackers = [tracker(self.state, passphrase) for tracker in TRACKERS]
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
            timestamp = int(time.time())
            await self.state.write(
                Query.insert_row(
                    PORTFOLIO_SNAPSHOT_TABLE_SCHEMA["table_name"],
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
                    PORTFOLIO_LOGS_TABLE_SCHEMA["table_name"],
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
        table = await self.state.read(
            Query.get_table(PORTFOLIO_SNAPSHOT_TABLE_SCHEMA["table_name"])
        )
        timestamp = table.get_column("timestamp")[int(index)]
        total_usd_value = table.get_column("total_usd_value")[int(index)]
        market_prices = table.get_column("market_prices")[int(index)]
        report = table.get_column("report")[int(index)]
        snapshot = print_snapshot_report(timestamp, total_usd_value, market_prices, report)  # type: ignore
        print(snapshot)
