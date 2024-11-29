from decimal import Decimal

from utils import CachedClass
from evm import EVM
from evm.constants import ABI
from evm.erc20 import ERC20
from dapps.aave.forks import FORKS


class AAVE(metaclass=CachedClass):
    def __init__(self, fork: str, chain: str) -> None:
        self.fork = fork
        self.chain = EVM.get_chain(chain)
        self.pool = self.chain.get_contract(
            FORKS[fork][self.chain.name]["pool_address"], ABI["AavePool"]
        )

    async def get_liquidation_threshold_for_a_token(
        self, a_token_address: str
    ) -> Decimal:
        a_token = self.chain.get_contract(a_token_address, ABI["AToken"])
        underlying_asset_address = await a_token.view(
            "UNDERLYING_ASSET_ADDRESS", immutable=True
        )
        config = await self.pool.view("getConfiguration", underlying_asset_address)
        bps = int(bin(config[0])[-32:-16], 2)
        return Decimal(bps) / Decimal("10000")

    async def get_supply_or_debt_amount(
        self, supply_or_debt_address: str, account: str
    ) -> Decimal:
        token = await self.chain.get_token(supply_or_debt_address)
        return await token.get_balance(account)
