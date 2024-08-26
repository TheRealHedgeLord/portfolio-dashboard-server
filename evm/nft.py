import asyncio

from web3 import AsyncWeb3
from eth_typing import ChecksumAddress
from eth_utils.address import to_checksum_address

from utils import CachedClass, InitializableClass, initialized_property
from evm.contract import Contract
from evm.constants import ABI


class ERC721(InitializableClass, metaclass=CachedClass):
    def __init__(
        self, network_id: int, rpc: AsyncWeb3, address: ChecksumAddress
    ) -> None:
        self.rpc = rpc
        self.address = address
        self.network_id = network_id
        self.contract = Contract(network_id, rpc, address, ABI["ERC721"])

    def __repr__(self) -> str:
        return f"<ERC721({self.address}) network_id: {self.network_id}>"

    async def _initialize(self) -> None:
        self._symbol, self._name = await asyncio.gather(
            self.contract.view("symbol", immutable=True),
            self.contract.view("name", immutable=True),
        )

    @property
    @initialized_property("_symbol")
    def symbol(self) -> str: ...

    @property
    @initialized_property("_name")
    def name(self) -> str: ...

    async def get_balance(self, address: str) -> int:
        return await self.contract.view("balanceOf", to_checksum_address(address))

    async def get_token_ids_by_owner(self, address: str) -> list[int]:
        balance = await self.get_balance(address)
        return list(
            await asyncio.gather(
                *[
                    self.contract.view("tokenOfOwnerByIndex", address, index)
                    for index in range(balance)
                ]
            )
        )
