from eth_utils.address import to_checksum_address
from eth_typing import ChecksumAddress

from utils import CachedClass
from clients.http import HTTPClient


class GMXPriceFeed:
    def __init__(self, data: dict) -> None:
        self._data = data

    def get_prices(self, market_prop: list[str | ChecksumAddress]) -> list[list]:
        return [
            self._data[to_checksum_address(token)]["price_prop"]
            for token in market_prop[1::]
        ]


class GMXOracle(HTTPClient, metaclass=CachedClass):
    _name = "GMXPriceOracle"
    _base_url = "https://arbitrum-v2-1-api.gmxinfra.io"
    _request_limit = 0.1

    async def get_price_feed(self) -> GMXPriceFeed:
        response = await self._call("get", "/signed_prices/latest")
        return GMXPriceFeed(
            {
                to_checksum_address(token["tokenAddress"]): {
                    "price_prop": [
                        int(token["maxPriceFull"]),
                        int(token["minPriceFull"]),
                    ],
                    "symbol": token["tokenSymbol"],
                }
                for token in response["signedPrices"]
            }
        )
