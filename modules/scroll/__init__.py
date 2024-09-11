import time
import hashlib

from eth_utils.address import to_checksum_address

from state import RDS
from state.sql import Query
from state.serializers import ColumnType
from dapps.scroll import Scroll


class ScrollMarksTracker:
    table_name = "scroll_marks_tracker"
    table_schema = {
        "timestamp": ColumnType.integer,
        "user_account_hash": ColumnType.bytes,
        "user_marks": ColumnType.decimal,
        "total_marks": ColumnType.decimal,
        "user_percentage": ColumnType.decimal,
    }

    def __init__(self, state: RDS) -> None:
        self.state = state
        self.scroll = Scroll()

    async def initialize_table(self) -> None:
        all_tables = await self.state.get_all_tables()
        if self.table_name not in all_tables:
            await self.state.write(
                Query.create_table(self.table_name, self.table_schema)
            )

    async def track_marks(self, user_account: str) -> None:
        account_hash = hashlib.sha256(
            to_checksum_address(user_account).encode()
        ).digest()
        data = await self.scroll.user_marks_analysis(user_account)
        row = {"timestamp": int(time.time()), "user_account_hash": account_hash}
        row.update(data)
        await self.state.write(Query.insert_row(self.table_name, row))

    async def get_table_for_user(self, user_account: str) -> None:
        account_hash = hashlib.sha256(
            to_checksum_address(user_account).encode()
        ).digest()
        table = await self.state.read(
            Query.get_table(
                self.table_name,
                columns=["timestamp", "user_marks", "total_marks", "user_percentage"],
                match_values={"user_account_hash": account_hash},
            )
        )
        print(table)
