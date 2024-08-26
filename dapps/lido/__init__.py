from decimal import Decimal

from utils import CachedClass
from evm import EVM
from evm.constants import ABI, ADDRESSES


class Lido(metaclass=CachedClass):
    def __init__(self) -> None:
        self.ethereum = EVM.get_chain("Ethereum")
        self.wsteth = self.ethereum.get_contract(
            ADDRESSES["Ethereum"]["wstETH"], ABI["wstETH"]
        )

    async def steth_per_wsteth(self) -> Decimal:
        steth_per_token = await self.wsteth.view("stEthPerToken")
        return Decimal(steth_per_token) / Decimal(10**18)
