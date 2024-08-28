import os
import time
import json
import hmac
import hashlib

from typing import Literal

from clients.http import HTTPClient
from state.relational.table import Table
from state.relational.serializers import ValueType
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
        return response["stdout"]

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
