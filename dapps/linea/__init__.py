import asyncio

from dapps.linea.lxpl import LineaSurgeAPI


class LineaPoints:
    def __init__(self) -> None:
        self.surge_api = LineaSurgeAPI()

    async def get_user_lxpl(self, user_account: str) -> dict:
        total_points, (user_points, user_rank) = await asyncio.gather(
            self.surge_api.get_total_points(),
            self.surge_api.get_points_for_address(user_account),
        )
        return {
            "user_points": user_points,
            "total_points": total_points,
            "user_rank": user_rank,
            "user_percentage": user_points / total_points,
        }
