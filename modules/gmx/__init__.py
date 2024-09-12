import time
import asyncio

from decimal import Decimal

from state import RDS
from state.sql import Query
from state.serializers import ColumnType
from evm import EVM
from dapps.gmx.gm import SupportedMarkets
from dapps.gmx.glv import SupportedGLV
from modules.gmx.optimizer import OptimizedGMX
from modules.gmx.constants import (
    SIMULATE_ASSET_AMOUNT,
    ALL_TRACKED_CHAINS,
    ALL_TRACKED_GM,
    ALL_TRACKED_GLV,
)


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
