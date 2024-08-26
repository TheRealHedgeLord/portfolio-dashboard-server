from decimal import Decimal

from utils import CachedClass
from svm import SVM
from dapps.jito.layout import JitoStakePool
from dapps.jito.constants import JITO_STAKE_POOL_PUBLIC_KEY
from exceptions import NotExistError


class Jito(metaclass=CachedClass):
    def __init__(self) -> None:
        self.solana = SVM()
        self.jito_stake_pool = self.solana.get_account(
            JITO_STAKE_POOL_PUBLIC_KEY, JitoStakePool
        )

    async def sol_per_jitosol(self) -> Decimal:
        jito_stake_pool_data = await self.jito_stake_pool.get_data()
        if not jito_stake_pool_data:
            raise NotExistError("JitoStakePool", JITO_STAKE_POOL_PUBLIC_KEY)
        return Decimal(jito_stake_pool_data["total_lamports"]) / Decimal(
            jito_stake_pool_data["pool_token_supply"]
        )
