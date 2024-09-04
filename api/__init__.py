import os
import time
import json
import hmac
import hashlib

from typing import Literal

from clients.http import HTTPClient
from state.relational.table import Table
from state.relational.serializers import ValueType, ColumnType
from api.serializers import to_cli_arg


class Client(HTTPClient):
    _name = "PortfolioDashboard"
    _base_url = os.environ["API_BASE_URL"]
    _request_limit = 0.1

    def __init__(self, api_key: str) -> None:
        super().__init__()
        self._api_key = api_key

    async def execute(self, option: str, method: str, *args: str) -> str:
        data = json.dumps(
            {
                "option": option,
                "method": method,
                "args": list(args),
                "timestamp": time.time(),
            }
        )
        signature = hmac.new(
            self._api_key.encode(), data.encode(), hashlib.sha256
        ).hexdigest()
        response = await self._call(
            "post",
            endpoint="/execute",
            data=data,
            headers={"signature": signature},
        )
        return response["content"][0:-1] if response["content"] else ""

    async def get_all_tables(self) -> list[str]:
        stdout = await self.execute("state_manager", "get_all_tables")
        return list(stdout.split(", "))

    async def get_table(
        self,
        table_name: str,
        columns: list[str] | Literal["*"] = "*",
        match_values: dict[str, ValueType] | None = None,
    ) -> Table:
        kwargs = {"columns": columns, "match_values": match_values}
        cli_kwargs = to_cli_arg(kwargs)
        stdout = await self.execute(
            "state_manager", "get_table", table_name, cli_kwargs
        )
        return Table.from_parsed(stdout)

    async def create_table(
        self, table_name: str, column_types: dict[str, ColumnType]
    ) -> None:
        cli_column_types = to_cli_arg(column_types)
        await self.execute(
            "state_manager", "create_table", table_name, cli_column_types
        )

    async def delete_table(self, table_name: str) -> None:
        await self.execute("state_manager", "delete_table", table_name)

    async def insert_row(
        self, table_name: str, column_values: dict[str, ValueType]
    ) -> None:
        cli_column_values = to_cli_arg(column_values)
        await self.execute("state_manager", "insert_row", table_name, cli_column_values)

    async def delete_rows(
        self, table_name: str, match_values: dict[str, ValueType] | None = None
    ) -> None:
        if match_values:
            cli_match_values = to_cli_arg(match_values)
            await self.execute(
                "state_manager", "delete_rows", table_name, cli_match_values
            )
        else:
            await self.execute("state_manager", "delete_rows", table_name)

    async def update_table(
        self,
        table_name: str,
        match_values: dict[str, ValueType],
        new_values: dict[str, ValueType],
    ) -> None:
        cli_match_values = to_cli_arg(match_values)
        cli_new_values = to_cli_arg(new_values)
        await self.execute(
            "state_manager",
            "update_table",
            table_name,
            cli_match_values,
            cli_new_values,
        )

    async def get_snapshot(self, index: int = -1) -> str:
        return await self.execute("portfolio", "get_snapshot", str(index))
