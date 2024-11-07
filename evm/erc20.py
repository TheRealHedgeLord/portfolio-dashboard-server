import asyncio

from decimal import Decimal

from web3 import AsyncWeb3
from eth_typing import ChecksumAddress
from eth_utils.address import to_checksum_address

from utils import CachedClass, InitializableClass, initialized_property
from evm.contract import Contract
from evm.constants import ABI


class ERC20(InitializableClass, metaclass=CachedClass):
    def __init__(
        self, network_id: int, rpc: AsyncWeb3, address: ChecksumAddress
    ) -> None:
        self.rpc = rpc
        self.address = address
        self.network_id = network_id
        self.contract = Contract(network_id, rpc, address, ABI["ERC20"])

    def __repr__(self) -> str:
        return f"<ERC20({self.address}) network_id: {self.network_id}>"

    async def _initialize(self) -> None:
        self._symbol, self._decimals, self._name = await asyncio.gather(
            self.contract.view("symbol", immutable=True),
            self.contract.view("decimals", immutable=True),
            self.contract.view("name", immutable=True),
        )

    @property
    @initialized_property("_decimals")
    def decimals(self) -> Decimal: ...

    @property
    @initialized_property("_symbol")
    def symbol(self) -> str: ...

    @property
    @initialized_property("_name")
    def name(self) -> str: ...

    async def get_balance(self, address: str) -> Decimal:
        balance = await self.contract.view("balanceOf", to_checksum_address(address))
        return Decimal(balance) / Decimal(10**self.decimals)
