from decimal import Decimal

from state.serializers import ColumnType
from modules.portfolio.assets import Coin
from modules.portfolio.trackers.base_tracker import BaseTracker
from dapps.benddao import ApeStaking


class BendDaoApeStakingTracker(BaseTracker):
    config_table_name = "benddao_ape_staking_tracker_config"
    config_table_schema = {
        "nft_address": ColumnType.string,
        "token_id": ColumnType.integer,
    }

    @property
    def staked_nfts(self) -> dict[str, list[int]]:
        staked_nfts = {}
        for nft_address, token_id in self.config.rows:
            if nft_address not in staked_nfts:
                staked_nfts[nft_address] = []
            staked_nfts[nft_address].append(token_id)
        return staked_nfts

    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]:
        ape_staking = ApeStaking()
        ape = Coin.get_coin("APE", "CoinGecko", {"token_id": "apecoin"}, "APE")
        balance = await ape_staking.get_claimable_ape(self.staked_nfts)
        display = await ape.display_balance(balance)
        usd = balance * await ape.price
        snapshot = {"BendDaoApeStaking": [f"Claimable {display}"]}
        platform_exposure = {"Ethereum": usd}
        sector_exposure = {"APE": usd}
        return usd, snapshot, platform_exposure, sector_exposure
