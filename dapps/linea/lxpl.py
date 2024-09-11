from decimal import Decimal

from utils import CachedClass
from clients.http import HTTPClient


class LineaSurgeAPI(HTTPClient, metaclass=CachedClass):
    _name = "LineaSurgeDashboard"
    _base_url = "https://kx58j6x5me.execute-api.us-east-1.amazonaws.com/linea"
    _request_limit = 0.1

    async def get_total_points(self) -> Decimal:
        response = await self._call("get", "/getLineaTotalPoints")
        return Decimal(response[-1]["total_xp"])

    async def get_points_for_address(self, address: str) -> tuple[Decimal, int]:
        leaderboard = await self._call("get", "/getLineaUserLeaderboard")
        index = 1
        for user in leaderboard:
            if user["user_address"].lower() == address.lower():
                return Decimal(user["xp"]), index
            index += 1
        raise Exception("user not found")
