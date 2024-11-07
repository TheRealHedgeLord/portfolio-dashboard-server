from __future__ import annotations

import asyncio

from decimal import Decimal

from utils import CachedClass, initialized_property
from evm import EVM
from evm.erc20 import ERC20
from evm.constants import ABI
from dapps.compound.forks import FORKS


class Compound(metaclass=CachedClass):
    @staticmethod
    async def get_fork(chain: str, fork: str) -> Compound:
        config = FORKS[fork][chain]
        instance = Compound(
            chain,
            fork,
            config["basic_lens_address"],
            config["comptroller_address"],
            config["token_address"],
        )
        await instance._initialize()
        return instance

    def __init__(
        self,
        chain: str,
        fork: str,
        basic_lens_addresses: str,
        comptroller_address,
        token_address: str,
    ) -> None:
        self.fork = fork
        self.chain = EVM.get_chain(chain)
        self.basic_lens = self.chain.get_contract(
            basic_lens_addresses, ABI["CompoundBasicLens"]
        )
        self.comptroller = self.chain.get_contract(
            comptroller_address, ABI["CompoundComptroller"]
        )
        self._token_address = token_address

    async def _initialize(self) -> None:
        self._token = await self.chain.get_token(self._token_address)

    @property
    @initialized_property("_token")
    def token(self) -> ERC20: ...

    async def get_claimable_rewards(self, address: str) -> Decimal:
        reward = await self.basic_lens.view(
            "rewardsAccrued", self.comptroller.address, address
        )
        return Decimal(reward[1][0]) / Decimal(10**self.token.decimals)

    async def get_supply_and_borrow_balance(
        self, ctoken_address: str, address: str
    ) -> tuple[Decimal, Decimal]:
        ctoken = self.chain.get_contract(ctoken_address, ABI["cToken"])
        (
            ctoken_balance,
            borrow_balance_stored,
            ctoken_exchange_rate,
            underlying_token_address,
        ) = await asyncio.gather(
            ctoken.view("balanceOf", address),
            ctoken.view("borrowBalanceStored", address),
            ctoken.view("exchangeRateStored"),
            ctoken.view("underlying", immutable=True),
        )
        underlying_token = await self.chain.get_token(underlying_token_address)
        rate = Decimal(ctoken_exchange_rate) / Decimal(
            10 ** (underlying_token.decimals + 18)
        )
        return Decimal(ctoken_balance) * rate, Decimal(borrow_balance_stored) / Decimal(
            10**underlying_token.decimals
        )

    async def get_collateral_factor(self, ctoken_address: str) -> Decimal:
        _, collateral_factor_mantissa, _ = await self.comptroller.view(
            "markets", ctoken_address
        )
        return Decimal(collateral_factor_mantissa) / Decimal(10**18)
