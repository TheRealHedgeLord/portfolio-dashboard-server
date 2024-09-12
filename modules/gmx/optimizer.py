import hashlib

from decimal import Decimal

from dapps.gmx import GMX
from dapps.gmx.gm import SupportedMarkets
from evm import EVM


class OptimizedGMX(GMX):
    def __init__(self, chain: EVM) -> None:
        super().__init__(chain)
        self._cache: dict[str, tuple[Decimal, Decimal, Decimal]] = {}

    async def get_gm_withdraw_amount_out(
        self, amount: Decimal, market: SupportedMarkets
    ) -> tuple[Decimal, Decimal]:
        key = hashlib.sha256(f"{self.chain.name}{market}".encode()).hexdigest()
        if key not in self._cache:
            long_token_amount, short_token_amount = (
                await super().get_gm_withdraw_amount_out(amount, market)
            )
            self._cache[key] = (long_token_amount, short_token_amount, amount)
            return long_token_amount, short_token_amount
        else:
            long_token_amount, short_token_amount, reference_amount = self._cache[key]
            return (
                long_token_amount * amount / reference_amount,
                short_token_amount * amount / reference_amount,
            )
