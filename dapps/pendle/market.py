import math
import time
import asyncio

from decimal import Decimal

from utils import CachedClass, InitializableClass, initialized_property
from evm import EVM
from evm.contract import Contract
from evm.constants import ABI


ROUTER_ADDRESS = "0x888888888889758F76e7103c6CbF23ABbF58F946"


class PendleMarket(InitializableClass, metaclass=CachedClass):
    def __init__(self, chain: str, market_address: str) -> None:
        self.chain = EVM.get_chain(chain)
        self.contract = self.chain.get_contract(market_address, ABI["PendleMarketV3"])

    async def _initialize(self) -> None:
        (_, pt_address, _), self._expiry = await asyncio.gather(
            self.contract.view("readTokens", immutable=True),
            self.contract.view("expiry", immutable=True),
        )
        self._pt = self.chain.get_contract(pt_address, ABI["PendlePrincipleToken"])
        _pt_name = await self._pt.view("name", immutable=True)
        self._name = _pt_name[3::]

    @property
    @initialized_property("_name")
    def name(self) -> str: ...

    @property
    @initialized_property("_expiry")
    def expiry(self) -> int: ...

    @property
    @initialized_property("_pt")
    def pt(self) -> Contract: ...

    async def _get_pt_balance(self, address: str) -> Decimal:
        balance = await self.pt.view("balanceOf", address)
        return Decimal(balance) / Decimal(10**18)

    async def _get_implied_rate(self) -> Decimal:
        state = await self.contract.view("readState", ROUTER_ADDRESS)
        ln_implied_rate = state[-1] / 10**18
        return Decimal(math.exp(ln_implied_rate) - 1)

    async def get_implied_apy(self) -> str:
        implied_rate = await self._get_implied_rate()
        return f"{round(implied_rate * Decimal(100),2)}%"

    def _get_market_value(self, face_value: Decimal, implied_rate: Decimal) -> Decimal:
        return face_value / (Decimal("1") + implied_rate) ** Decimal(
            (self.expiry - time.time()) / (365 * 24 * 60 * 60)
        )

    async def get_pt_market_value(self, address: str) -> Decimal:
        face_value, implied_rate = await asyncio.gather(
            self._get_pt_balance(address), self._get_implied_rate()
        )
        return self._get_market_value(face_value, implied_rate)
