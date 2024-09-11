import time
import hashlib

from typing import Literal
from eth_utils.address import to_checksum_address

from state import RDS
from state.sql import Query
from state.serializers import ColumnType
from dapps.linea import LineaPoints


class LineaPointsTracker:
    table_name = "linea_points_tracker"
    table_schema = {
        "timestamp": ColumnType.integer,
        "user_account_hash": ColumnType.bytes,
        "points_type": ColumnType.string,
        "user_points": ColumnType.decimal,
        "total_points": ColumnType.decimal,
        "user_rank": ColumnType.integer,
        "user_percentage": ColumnType.decimal,
    }

    def __init__(self, state: RDS) -> None:
        self.state = state
        self.linea = LineaPoints()

    async def initialize_table(self) -> None:
        all_tables = await self.state.get_all_tables()
        if self.table_name not in all_tables:
            await self.state.write(
                Query.create_table(self.table_name, self.table_schema)
            )

    async def track_points(
        self, user_account: str, points_type: Literal["LXP", "LXP-L"]
    ) -> None:
        account_hash = hashlib.sha256(
            to_checksum_address(user_account).encode()
        ).digest()
        if points_type == "LXP-L":
            data = await self.linea.get_user_lxpl(user_account)
            row = {
                "timestamp": int(time.time()),
                "user_account_hash": account_hash,
                "points_type": points_type,
            }
            row.update(data)
            await self.state.write(Query.insert_row(self.table_name, row))

    async def get_table_for_user(
        self, user_account: str, points_type: Literal["LXP", "LXP-L"]
    ) -> None:
        account_hash = hashlib.sha256(
            to_checksum_address(user_account).encode()
        ).digest()
        table = await self.state.read(
            Query.get_table(
                self.table_name,
                columns=[
                    "timestamp",
                    "user_points",
                    "total_points",
                    "user_rank",
                    "user_percentage",
                ],
                match_values={
                    "user_account_hash": account_hash,
                    "points_type": points_type,
                },
            )
        )
        print(table)
