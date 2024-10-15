import time
import hashlib

from datetime import datetime
from eth_utils.address import to_checksum_address

from state import RDS
from state.table import Table
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

    async def _get_table_for_user(self, user_account: str) -> Table:
        account_hash = hashlib.sha256(
            to_checksum_address(user_account).encode()
        ).digest()
        return await self.state.read(
            Query.get_table(
                self.table_name,
                columns=["timestamp", "user_marks", "total_marks", "user_percentage"],
                match_values={"user_account_hash": account_hash},
            )
        )

    async def get_table_for_user(self, user_account: str) -> None:
        table = await self._get_table_for_user(user_account)
        print(table)

    async def predict(
        self,
        user_account: str,
        year: str,
        month: str,
        day: str,
        slope_start_index: str = "-3",
    ) -> None:
        target_time = int(datetime(int(year), int(month), int(day)).timestamp())
        table = await self._get_table_for_user(user_account)
        slope_delta_time = (
            table.get_column("timestamp")[-1]
            - table.get_column("timestamp")[int(slope_start_index)]
        )  # type: ignore
        slope_user_marks = (
            table.get_column("user_marks")[-1]
            - table.get_column("user_marks")[int(slope_start_index)]
        ) / slope_delta_time  # type: ignore
        slope_total_marks = (
            table.get_column("total_marks")[-1]
            - table.get_column("total_marks")[int(slope_start_index)]
        ) / slope_delta_time  # type: ignore
        delta_time = target_time - table.get_column("timestamp")[-1]  # type: ignore
        target_user_marks = (
            table.get_column("user_marks")[-1] + slope_user_marks * delta_time  # type: ignore
        )
        target_total_marks = (
            table.get_column("total_marks")[-1] + slope_total_marks * delta_time  # type: ignore
        )
        target_user_percentage = round(target_user_marks * 100 / target_total_marks, 5)  # type: ignore
        print(f"Prediction (mm/dd/yyyy): {month}/{day}/{year}")
        print(f"User marks: {target_user_marks}")
        print(f"Total marks: {target_total_marks}")
        print(f"User percentage: {target_user_percentage}%")
