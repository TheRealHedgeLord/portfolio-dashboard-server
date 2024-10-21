from decimal import Decimal

from evm import EVM
from evm.constants import ADDRESSES, ABI


class ApeStaking:
    def __init__(self) -> None:
        ethereum = EVM.get_chain("Ethereum")
        self.bend_nft_pool = ethereum.get_contract(
            ADDRESSES[ethereum.name]["BendNftPool"], ABI["BendNftPool"]
        )

    async def get_claimable_ape(self, staked_nfts: dict[str, list[int]]) -> Decimal:
        nfts = [nft for nft in staked_nfts]
        token_ids = [staked_nfts[nft] for nft in staked_nfts]
        claimable_ape = await self.bend_nft_pool.view("claimable", nfts, token_ids)
        return Decimal(claimable_ape) / Decimal(10**18)
