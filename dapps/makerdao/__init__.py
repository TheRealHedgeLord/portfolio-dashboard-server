from decimal import Decimal

from utils import CachedClass
from evm import EVM
from evm.constants import ABI, ADDRESSES


class MakerDAO(metaclass=CachedClass):
    def __init__(self) -> None:
        self.ethereum = EVM.get_chain("Ethereum")
        self.sdai = self.ethereum.get_contract(
            ADDRESSES["Ethereum"]["sDAI"], ABI["sDAI"]
        )

    async def dai_per_sdai(self) -> Decimal:
        preview_redeem_1_sdai = await self.sdai.view("previewRedeem", 10**18)
        return Decimal(preview_redeem_1_sdai) / Decimal(10**18)
