from typing import Any

from state import RDS
from state.sql import Query
from state.serializers import ColumnType


class Cache:
    _data = {}
    _table_name = "cache"
    _table_schema = {"cache_key": ColumnType.string, "cache_value": ColumnType.json}

    @staticmethod
    def get(key) -> Any:
        return Cache._data.get(key)

    @staticmethod
    def put(key, value) -> None:
        Cache._data[key] = value

    @staticmethod
    async def read_from_state(state: RDS) -> None:
        Cache._state = state
        all_tables = await Cache._state.get_all_tables()
        if Cache._table_name not in all_tables:
            await Cache._state.write(
                Query.create_table(Cache._table_name, Cache._table_schema)
            )
        Cache._table = await Cache._state.read(Query.get_table(Cache._table_name))
        Cache._data = {
            Cache._table.get_column("cache_key")[i]: Cache._table.get_column(
                "cache_value"
            )[i]
            for i in range(Cache._table.row_count)
        }

    @staticmethod
    async def save() -> None:
        if hasattr(Cache, "_state") and hasattr(Cache, "_table"):
            rows = [
                [key, Cache._data[key]]
                for key in Cache._data
                if key not in Cache._table.get_column("cache_key")
            ]
            if len(rows) > 0:
                await Cache._state.write(
                    Query.insert_rows(Cache._table_name, ["cache_key", "cache_value"], rows)  # type: ignore
                )
                Cache._table = await Cache._state.read(
                    Query.get_table(Cache._table_name)
                )
