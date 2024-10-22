from decimal import Decimal

from evm import EVM
from evm.constants import ADDRESSES, ABI
from utils import CachedClass


class SUSDS(metaclass=CachedClass):
    def __init__(self) -> None:
        ethereum = EVM.get_chain("Ethereum")
        self.contract = ethereum.get_contract(
            ADDRESSES[ethereum.name]["sUSDS"], ABI["SUsds"]
        )

    async def usds_per_susds(self) -> Decimal:
        usds = await self.contract.view("previewRedeem", 10**18)
        return Decimal(usds) / Decimal(10**18)
