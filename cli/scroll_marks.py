import time

from datetime import datetime

from state.relational import RelationalDatabase
from state.relational.sql import Query
from dapps.scroll import Scroll


_database = RelationalDatabase()
_scroll = Scroll()

_table = "scroll_marks"
if _table not in _database.get_all_tables():
    _database.write(
        Query.create_table(
            _table,
            {
                "timestamp": "integer",
                "total_marks": "decimal",
                "user_marks": "decimal",
                "user_percentage": "decimal",
            },
        )
    )


async def track_marks(wallet_address: str) -> None:
    user_data = await _scroll.user_marks_analysis(wallet_address)
    timestamp = int(time.time())
    _database.write(Query.insert_row(_table, {"timestamp": timestamp, **user_data}))


async def show_data() -> None:
    table = _database.read(Query.get_table(_table))
    print(table)


async def predict(year: str, month: str, date: str) -> None:
    at_timestamp = int(datetime(int(year), int(month), int(date)).timestamp())
    table = _database.read(Query.get_table(_table))
    user_marks_delta = (
        table.get_column("user_marks")[-1] - table.get_column("user_marks")[0]
    ) / (  # type: ignore
        table.get_column("timestamp")[-1] - table.get_column("timestamp")[0]
    )  # type: ignore
    total_marks_delta = (
        table.get_column("total_marks")[-1] - table.get_column("total_marks")[0]
    ) / (  # type: ignore
        table.get_column("timestamp")[-1] - table.get_column("timestamp")[0]
    )  # type: ignore
    remaining_time = at_timestamp - table.get_column("timestamp")[-1]  # type: ignore
    final_user_marks = (
        table.get_column("user_marks")[-1] + remaining_time * user_marks_delta  # type: ignore
    )
    final_total_marks = (
        table.get_column("total_marks")[-1] + remaining_time * total_marks_delta  # type: ignore
    )
    final_ratio = final_user_marks / final_total_marks  # type: ignore
    print("Remaining Time:", remaining_time // (24 * 60 * 60), "days")
    print("Final User Marks:", final_user_marks)
    print("final Total Marks:", final_total_marks)
    print("Final User Share:", f"{round(final_ratio*100, 5)}%")


methods = {"track_marks": track_marks, "show_data": show_data, "predict": predict}
