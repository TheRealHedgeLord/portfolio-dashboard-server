from decimal import Decimal

from utils import CachedClass
from bitcoin.hiro import HiroClient
from bitcoin.mempool import MempoolClient
from bitcoin.constants import ORDINALS
from exceptions import NotExistError


def find_ordinal_by_inscription_id(inscription_id: int) -> str | None:
    for ordinal in ORDINALS:
        lower, upper = ORDINALS[ordinal]
        if lower <= inscription_id <= upper:
            return ordinal


class Bitcoin(metaclass=CachedClass):
    def __init__(self) -> None:
        self.hiro_client = HiroClient()
        self.mempool_client = MempoolClient()

    async def get_wallet_balance(self, wallet_address: str) -> Decimal:
        return await self.mempool_client.get_wallet_balance(wallet_address)

    async def get_wallet_ordinals(self, wallet_address: str) -> dict[str, int]:
        inscriptions = await self.hiro_client.get_ordinals(wallet_address)
        ordinals = {}
        for inscription_id in inscriptions:
            ordinal = find_ordinal_by_inscription_id(inscription_id)
            if ordinal in ordinals:
                ordinals[ordinal] += 1
            elif ordinal:
                ordinals[ordinal] = 1
        return ordinals

    async def get_ordinal_balance(self, wallet_address: str, ordinal: str) -> int:
        inscriptions = await self.hiro_client.get_ordinals(wallet_address)
        balance = 0
        lower, upper = ORDINALS[ordinal]
        for inscription_id in inscriptions:
            if lower <= inscription_id <= upper:
                balance += 1
        return balance
