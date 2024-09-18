import os

from decimal import Decimal

from evm import EVM
from evm.constants import ADDRESSES, ABI
from web2.coingecko import CoinGecko


SKY_PER_MKR = 24000


class Sky:
    def __init__(self) -> None:
        self.ethereum = EVM.get_chain("Ethereum")
        self.staking_reward_contract = self.ethereum.get_contract(
            ADDRESSES["Ethereum"]["USDSStakingReward"], ABI["USDSStakingReward"]
        )
        self.coingecko = CoinGecko(os.environ["COINGECKO_API_KEY"])

    async def sky_price_from_mkr(self) -> Decimal:
        price, _ = (await self.coingecko.get_token_data("maker"))[0]
        return price / SKY_PER_MKR

    async def get_staked_usds(self, account: str) -> Decimal:
        usds = await self.staking_reward_contract.view("balanceOf", account)
        return Decimal(usds) / Decimal(10**18)

    async def get_sky_reward(self, account: str) -> Decimal:
        sky = await self.staking_reward_contract.view("earned", account)
        return Decimal(sky) / Decimal(10**18)
