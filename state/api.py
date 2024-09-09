import os
import time
import json
import hmac
import hashlib

from typing import Any

from clients.http import HTTPClient
from utils import CachedClass


class APIGatewayClient(HTTPClient, metaclass=CachedClass):
    _name = "RDS"
    _base_url = os.environ["RDS_API_BASE_URL"]
    _request_limit = 0.001

    def __init__(self, api_key: str) -> None:
        super().__init__()
        self._api_key = api_key

    async def call(self, method: str, *args: str) -> dict:
        data = json.dumps(
            {
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
            endpoint="/rds",
            data=data,
            headers={"signature": signature},
        )
        return response

    async def get_all_tables(self) -> list[str]:
        response = await self.call("get_all_tables")
        return response["data"]

    async def read(self, command: str) -> tuple[list[str], list[list[int | str]]]:
        response = await self.call("read", command)
        return response["data"][0], response["data"][1]

    async def write(self, command: str) -> None:
        await self.call("write", command)
