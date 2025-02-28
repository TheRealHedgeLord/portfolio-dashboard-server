from decimal import Decimal

from utils import CachedClass
from evm import EVM, to_checksum_address
from evm.constants import ABI, ADDRESSES


class sUSDe(metaclass=CachedClass):
    def __init__(self) -> None:
        self.ethereum = EVM.get_chain("Ethereum")
        self.contract = self.ethereum.get_contract(
            ADDRESSES[self.ethereum.name]["sUSDe"], ABI["sUSDe"]
        )

    async def get_pending_withdrawal(self, address: str) -> tuple[Decimal, int]:
        time, usde_raw = await self.contract.view(
            "cooldowns", to_checksum_address(address)
        )
        return Decimal(usde_raw) / Decimal(10**18), time
