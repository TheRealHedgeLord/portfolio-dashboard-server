from __future__ import annotations

import asyncio
from decimal import Decimal

from utils import CachedClass, InitializableClass
from evm import EVM
from evm.token import ERC20
from evm.constants import ABI
from dapps.math import ClassicPool
from exceptions import InvalidValue


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
    ) -> ClassicPool:
        reserve_0, reserve_1 = await asyncio.gather(
            self.contract.view("balances", 0), self.contract.view("balances", 1)
        )
        if base_token == self.token_0 and quote_token == self.token_1:
            return ClassicPool(
                Decimal(reserve_0) / Decimal(10**self.token_0.decimals),
                Decimal(reserve_1) / Decimal(10**self.token_1.decimals),
            )
        elif base_token == self.token_1 and quote_token == self.token_0:
            return ClassicPool(
                Decimal(reserve_1) / Decimal(10**self.token_1.decimals),
                Decimal(reserve_0) / Decimal(10**self.token_0.decimals),
            )
        else:
            raise InvalidValue("reserve tokens", f"({base_token}, {quote_token})")
