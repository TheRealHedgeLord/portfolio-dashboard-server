from __future__ import annotations

import asyncio

from utils import CachedClass, InitializableClass
from evm import to_checksum_address, EVM
from evm.token import ERC20
from evm.constants import ABI
from dapps.math import ClassicPool


class CurveClassicPool(InitializableClass, metaclass=CachedClass):
    @staticmethod
    async def get_pool(chain: EVM, address: str) -> CurveClassicPool:
        instance = CurveClassicPool(chain, address)
        await instance.initialize()
        return instance

    def __init__(self, chain: EVM, address: str) -> None:
        self.chain = chain
        self.contract = chain.get_contract(address, ABI["CurveClassicPool"])

    async def _initialize(self) -> None:
        token_0, token_1 = await asyncio.gather(
            self.contract.view("coins", 0, immutable=True),
            self.contract.view("coins", 1, immutable=True),
        )
        self.token_0, self.token_1 = await asyncio.gather(
            self.chain.get_token(token_0), self.chain.get_token(token_1)
        )

    async def get_reserve_data(
        self, base_token: ERC20, quote_token: ERC20
    ) -> ClassicPool: ...
