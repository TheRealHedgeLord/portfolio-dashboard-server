import os
import time
import uuid
import traceback
import asyncio

from decimal import Decimal

from utils import dict_add, to_json
from state.relational import RelationalDatabase
from state.relational.sql import Query
from cli.portfolio.modules.coin_portfolio import CoinPortfolio
from cli.portfolio.modules.compound_portfolio import CompoundPortfolio
from cli.portfolio.modules.gmx_portfolio import GMXPortfolio
from cli.portfolio.modules.nft_portfolio import NFTPortfolio
from cli.portfolio.context import btc_price, eth_price, sol_price
from cli.portfolio.display import print_snapshot_report
from web2.telegram import TelegramBot

_ALL_MODULES = [CoinPortfolio, CompoundPortfolio, GMXPortfolio, NFTPortfolio]

_database = RelationalDatabase()

_PORTFOLIO_SNAPSHOT_TABLE_NAME = "portfolio_snapshots"

if _PORTFOLIO_SNAPSHOT_TABLE_NAME not in _database.get_all_tables():
    _database.write(
        Query.create_table(
            _PORTFOLIO_SNAPSHOT_TABLE_NAME,
            {
                "timestamp": "integer",
                "market_prices": "json",
                "total_usd_value": "decimal",
                "report": "json",
                "platform_exposure": "json",
                "sector_exposure": "json",
            },
        )
    )

_PORTFOLIO_LOGS_TABLE_NAME = "portfolio_logs"

if _PORTFOLIO_LOGS_TABLE_NAME not in _database.get_all_tables():
    _database.write(
        Query.create_table(
            _PORTFOLIO_LOGS_TABLE_NAME,
            {
                "timestamp": "integer",
                "error_id": "string",
                "stack_trace": "string",
            },
        )
    )


async def take_snapshot(passphrase: str) -> None:
    try:
        btc, eth, sol = await asyncio.gather(btc_price(), eth_price(), sol_price())
        market_prices = {"BTC": btc, "ETH": eth, "SOL": sol}
        all_modules_snapshots = await asyncio.gather(
            *[module(passphrase).get_snapshot() for module in _ALL_MODULES]
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
        _database.write(
            Query.insert_row(
                _PORTFOLIO_SNAPSHOT_TABLE_NAME,
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
        error_id = uuid.uuid4().hex
        stack_trace = traceback.format_exc()
        _database.write(
            Query.insert_row(
                _PORTFOLIO_LOGS_TABLE_NAME,
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


async def get_snapshot(index: str = "-1") -> None:
    table = _database.read(Query.get_table(_PORTFOLIO_SNAPSHOT_TABLE_NAME))
    timestamp = table.get_column("timestamp")[int(index)]
    total_usd_value = table.get_column("total_usd_value")[int(index)]
    market_prices = table.get_column("market_prices")[int(index)]
    report = table.get_column("report")[int(index)]
    print_snapshot_report(timestamp, total_usd_value, market_prices, report)  # type: ignore


methods = {"take_snapshot": take_snapshot, "get_snapshot": get_snapshot}
