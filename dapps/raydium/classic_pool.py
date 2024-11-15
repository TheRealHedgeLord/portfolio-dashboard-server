from __future__ import annotations

from decimal import Decimal

from utils import InitializableClass, CachedClass, initialized_property
from dapps.math import ClassicPool
from dapps.raydium.layout import RaydiumPairClassic
from svm import SVM
from svm.account import Account
from svm.token import SPLToken
from svm.layout.spl import TokenAccount
from exceptions import InvalidValue


class RaydiumClassicPool(InitializableClass, metaclass=CachedClass):
    @staticmethod
    async def get_pool(address: str) -> RaydiumClassicPool:
        instance = RaydiumClassicPool(address)
        await instance.initialize()
        return instance

    def __init__(self, address: str) -> None:
        self.address = address
        self.solana = SVM()
        self.account = self.solana.get_account(address, RaydiumPairClassic)

    @property
    @initialized_property("_base_mint")
    def base_mint(self) -> str: ...

    @property
    @initialized_property("_quote_mint")
    def quote_mint(self) -> str: ...

    @property
    @initialized_property("_base_vault")
    def base_vault(self) -> Account: ...

    @property
    @initialized_property("_quote_vault")
    def quote_vault(self) -> Account: ...

    async def _initialize(self) -> None:
        data = await self.account.get_data()
        self._base_mint = data["base_mint"]
        self._quote_mint = data["quote_mint"]
        self._base_vault = self.solana.get_account(data["base_vault"], TokenAccount)
        self._quote_vault = self.solana.get_account(data["quote_vault"], TokenAccount)

    async def get_reserve_data(
        self, base_token: SPLToken, quote_token: SPLToken
    ) -> ClassicPool:
        if base_token.mint == self.base_mint and quote_token.mint == self.quote_mint:
            base_reserve = await self.base_vault.get_data()
            quote_reserve = await self.quote_vault.get_data()
            return ClassicPool(
                base_reserve["amount"] / Decimal(10**base_token.decimals),
                quote_reserve["amount"] / Decimal(10**quote_token.decimals),
            )
        elif base_token.mint == self.quote_mint and quote_token.mint == self.base_mint:
            base_reserve = await self.quote_vault.get_data()
            quote_reserve = await self.base_vault.get_data()
            return ClassicPool(
                base_reserve["amount"] / Decimal(10**base_token.decimals),
                quote_reserve["amount"] / Decimal(10**quote_token.decimals),
            )
        else:
            raise InvalidValue("reserve tokens", f"({base_token}, {quote_token})")
