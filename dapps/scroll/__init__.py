from decimal import Decimal

from utils import CachedClass
from dapps.scroll.marks import ScrollMarksAPI


class Scroll(metaclass=CachedClass):
    def __init__(self) -> None:
        self.marks_api = ScrollMarksAPI()

    async def get_total_marks(self) -> Decimal:
        return await self.marks_api.get_total_marks()

    async def get_marks(self, wallet_address: str) -> Decimal:
        return await self.marks_api.get_marks(wallet_address)

    async def user_marks_analysis(self, wallet_address: str) -> dict[str, Decimal]:
        user_marks = await self.marks_api.get_marks(wallet_address)
        total_marks = await self.get_total_marks()
        user_percentage = user_marks / total_marks
        return {
            "user_marks": user_marks,
            "total_marks": total_marks,
            "user_percentage": user_percentage,
        }
