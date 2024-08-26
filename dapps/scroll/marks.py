from decimal import Decimal

from utils import CachedClass
from clients.http import HTTPClient


class ScrollMarksAPI(HTTPClient, metaclass=CachedClass):
    _name = "ScrollSessions"
    _base_url = "https://kx58j6x5me.execute-api.us-east-1.amazonaws.com"
    _request_limit = 0.1

    async def get_marks(self, wallet_address: str) -> Decimal:
        response = await self._call(
            "get", "/scroll/wallet-points", parameters={"walletAddress": wallet_address}
        )
        return Decimal(str(response[0]["points"]))

    async def get_total_marks(self) -> Decimal:
        response = await self._call("get", "/scroll/total-points")
        return Decimal(str(response[0]["total_points"]))
