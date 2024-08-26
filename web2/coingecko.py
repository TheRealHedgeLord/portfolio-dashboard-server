from decimal import Decimal

from clients.http import HTTPClient
from utils import CachedClass


class CoinGecko(HTTPClient, metaclass=CachedClass):
    _name = "CoinGecko"
    _base_url = "https://api.coingecko.com"
    _request_limit = 3.5

    def __init__(self, api_key: str) -> None:
        super().__init__()
        self._api_key = api_key

    @property
    def _headers(self) -> dict:
        return {"accept": "application/json", "x-cg-demo-api-key": self._api_key}

    async def get_token_data(self, *token_ids: str) -> list[tuple[Decimal, Decimal]]:
        response = await self._call(
            "get",
            "/api/v3/simple/price",
            parameters={
                "ids": ",".join(token_ids),
                "vs_currencies": "usd",
                "include_market_cap": "true",
            },
            headers=self._headers,
        )
        return [
            (
                Decimal(str(response[token]["usd"])),
                Decimal(str(response[token]["usd_market_cap"])),
            )
            for token in token_ids
        ]

    async def get_nft_price(self, nft_id: str) -> Decimal:
        response = await self._call(
            "get",
            f"/api/v3/nfts/{nft_id}",
            headers=self._headers,
        )
        return Decimal(response["floor_price"]["native_currency"])
