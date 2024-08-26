import asyncio

from decimal import Decimal

from evm import EVM
from utils import CachedClass
from dapps.gmx.oracle import GMXOracle
from evm.constants import ABI, ADDRESSES
from dapps.gmx.gm import SupportedMarkets, MARKETS


class GMX(metaclass=CachedClass):
    oracle = GMXOracle()

    def __init__(self, chain: EVM) -> None:
        self.chain = chain
        self.gmx_reader = chain.get_contract(
            ADDRESSES[chain.name]["GMXReader"], ABI["GMXReader"]
        )
        self.data_store = ADDRESSES[chain.name]["GMXDataStore"]
        self.gmx_ui_fee_receiver = ADDRESSES[chain.name]["GMXUiFeeReciever"]
        self.staked_gmx_tracker = self.chain.get_contract(
            ADDRESSES[chain.name]["StakedGMXTracker"], ABI["StakedGMXTracker"]
        )
        self.sbfgmx = self.chain.get_contract(
            ADDRESSES[chain.name]["sbfGMX"], ABI["StakedGMXTracker"]
        )
        self.vGMX = self.chain.get_contract(
            ADDRESSES[chain.name]["vGMX"], ABI["StakedGMXTracker"]
        )

    async def get_gm_withdraw_amount_out(
        self, amount: Decimal, market: SupportedMarkets
    ) -> tuple[Decimal, Decimal]:
        gm_market = MARKETS[self.chain.name][market]
        market_prop = gm_market["market_prop"]
        price_feed = await self.oracle.get_price_feed()
        long, short = await self.gmx_reader.view(
            "getWithdrawalAmountOut",
            self.data_store,
            market_prop,
            price_feed.get_prices(market_prop),
            int(amount * Decimal(10**18)),
            self.gmx_ui_fee_receiver,
        )
        return Decimal(long) / Decimal(10 ** gm_market["long_token_decimal"]), Decimal(
            short
        ) / Decimal(10 ** gm_market["short_token_decimal"])

    async def get_gm_withdraw_amount_out_for_account(
        self, account: str, market: SupportedMarkets
    ) -> tuple[Decimal, Decimal]:
        gm = await self.chain.get_token(
            MARKETS[self.chain.name][market]["market_prop"][0]
        )
        balance = await gm.get_balance(account)
        return await self.get_gm_withdraw_amount_out(balance, market)

    async def get_gmx_staking(self, account: str) -> tuple[Decimal, Decimal, Decimal]:
        staked_gmx, reward_gmx, reward_eth = await asyncio.gather(
            self.staked_gmx_tracker.view("stakedAmounts", account),
            self.vGMX.view("claimable", account),
            self.sbfgmx.view("claimable", account),
        )
        return (
            Decimal(staked_gmx) / Decimal(10**18),
            Decimal(reward_gmx) / Decimal(10**18),
            Decimal(reward_eth) / Decimal(10**18),
        )
