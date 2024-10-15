import time
import hmac
import hashlib

from decimal import Decimal
from urllib.parse import urlencode

from clients.http import HTTPClient
from utils import CachedClass


class Binance(HTTPClient, metaclass=CachedClass):
    _name = "Binance"
    _base_url = "https://api.binance.com"
    _request_limit = 0.1

    def __init__(
        self, api_key: str | None = None, secret_key: str | None = None
    ) -> None:
        super().__init__()
        self._api_key = api_key
        self._secret_key = secret_key.encode() if secret_key else b""

    def _sign(self, params: dict) -> None:
        signature = hmac.new(
            self._secret_key, urlencode(params).encode(), hashlib.sha256
        ).hexdigest()
        params.update({"signature": signature})

    @property
    def _headers(self) -> dict:
        return {"X-MBX-APIKEY": self._api_key}

    async def get_all_balance(self) -> dict[str, Decimal]:
        params = {"timestamp": int(time.time() * 1000), "recvWindow": 6000}
        self._sign(params)
        data = await self._call(
            "get", endpoint="/api/v3/account", parameters=params, headers=self._headers
        )
        return {
            asset["asset"]: Decimal(asset["free"]) + Decimal(asset["locked"])
            for asset in data["balances"]
            if Decimal(asset["free"]) + Decimal(asset["locked"]) > Decimal("0")
        }

    async def get_token_balance(self, token_ticker: str) -> Decimal:
        all_balance = await self.get_all_balance()
        return all_balance[token_ticker]

    async def last_traded_price(self, ticker: str) -> Decimal:
        data = await self._call(
            "get", endpoint="/api/v3/ticker/price", parameters={"symbol": ticker}
        )
        return Decimal(data["price"])
