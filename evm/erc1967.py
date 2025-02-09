from web3 import AsyncWeb3
from eth_typing import ChecksumAddress

from utils import CachedClass


IMPLEMENTATION_SLOT = int(
    "360894a13ba1a3210667c828492db98dca3e2076cc3735a920a3ca505d382bbc", 16
)
ADMIN_SLOT = int("b53127684a568b3173ae13b9f8a6016e243e63b6e8ee1178d6a717850b5d6103", 16)


class ERC1967(metaclass=CachedClass):
    def __init__(
        self, network_id: int, rpc: AsyncWeb3, address: ChecksumAddress
    ) -> None:
        self.rpc = rpc
        self.address = address
        self.network_id = network_id

    async def get_implementation_address(self) -> str:
        address_bytes = await self.rpc.eth.get_storage_at(
            self.address, IMPLEMENTATION_SLOT
        )
        return "0x" + address_bytes.hex()[-40::]

    async def get_admin_address(self) -> str:
        address_bytes = await self.rpc.eth.get_storage_at(self.address, ADMIN_SLOT)
        return "0x" + address_bytes.hex()[-40::]
