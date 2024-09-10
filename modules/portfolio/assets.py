from __future__ import annotations


from decimal import Decimal

from modules.portfolio.context import (
    btc_price,
    eth_price,
    sol_price,
    coingecko_price,
    coingecko_nft_price,
    wsteth,
    jitosol,
    sdai,
)
from modules.portfolio.display import (
    display_btc_asset,
    display_eth_asset,
    display_sol_asset,
    display_stable_coins,
    display_nft,
    display_asset,
)
from svm import SVM
from evm import EVM
from bitcoin import Bitcoin
from exceptions import NotExistError


class Coin:
    _instances: dict[str, Coin] = {}

    @staticmethod
    def get_coin_by_ticker(ticker: str) -> Coin:
        if ticker not in Coin._instances:
            raise NotExistError("Coin", ticker)
        else:
            return Coin._instances[ticker]

    @staticmethod
    def get_coin(
        ticker: str,
        price_reference: str,
        price_reference_config: dict,
        sector: str,
    ) -> Coin:
        if ticker in Coin._instances:
            instance = Coin._instances[ticker]
            if (
                price_reference != instance.price_reference
                or price_reference_config != instance.price_reference_config
                or sector != instance.sector
            ):
                raise Exception("conflicting coin config")
        else:
            instance = Coin(ticker, price_reference, price_reference_config, sector)
            Coin._instances[ticker] = instance
        return instance

    def __init__(
        self,
        ticker: str,
        price_reference: str,
        price_reference_config: dict,
        sector: str,
    ):
        if ticker in Coin._instances:
            raise Exception(
                "please use Coin.get_coin or Coin.get_coin_by_ticker to get an instance"
            )
        self.ticker = ticker
        self.price_reference = price_reference
        self.price_reference_config = price_reference_config
        self.sector = sector

    async def get_balance(
        self, platform: str, asset_id: str, account: str | dict
    ) -> Decimal:
        if isinstance(account, dict):
            ...
        elif platform == "Bitcoin":
            bitcoin = Bitcoin()
            if asset_id == "native":
                balance = await bitcoin.get_wallet_balance(account)
        elif platform == "Solana":
            solana = SVM()
            if asset_id == "native":
                balance = await solana.get_balance(account)
            else:
                spl = await solana.get_token(asset_id)
                balance = await spl.get_balance(account)
        else:
            evm_chain = EVM.get_chain(platform)
            if asset_id == "native":
                balance = await evm_chain.get_balance(account)
            else:
                erc20 = await evm_chain.get_token(asset_id)
                balance = await erc20.get_balance(account)
        return await self.get_adjusted_balance(balance)

    async def get_adjusted_balance(self, balance: Decimal) -> Decimal:
        if self.price_reference == "wstETH":
            multiplier = await wsteth()
            return balance * multiplier
        elif self.price_reference == "jitoSOL":
            multiplier = await jitosol()
            return balance * multiplier
        elif self.price_reference == "sDAI":
            multiplier = await sdai()
            return balance * multiplier
        else:
            return balance

    @property
    async def price(self) -> Decimal:
        if self.price_reference == "BTC":
            return await btc_price()
        elif self.price_reference in ["ETH", "wstETH"]:
            return await eth_price()
        elif self.price_reference in ["SOL", "jitoSOL"]:
            return await sol_price()
        elif self.price_reference in ["USD", "sDAI"]:
            return Decimal("1")
        elif self.price_reference == "CoinGecko":
            return await coingecko_price(self.price_reference_config["token_id"])
        else:
            raise NotExistError("price_reference", self.price_reference)

    async def display_balance(self, balance: Decimal) -> str:
        price = await self.price
        usd_value = price * balance
        if self.sector == "BTC":
            return display_btc_asset(self.ticker, balance, usd_value)
        elif self.sector == "ETH":
            return display_eth_asset(self.ticker, balance, usd_value)
        elif self.sector == "SOL":
            return display_sol_asset(self.ticker, balance, usd_value)
        elif self.sector == "StableCoins":
            return display_stable_coins(self.ticker, usd_value)
        else:
            return display_asset(self.ticker, balance, price, usd_value)


class NFT:
    _instances: dict[str, NFT] = {}

    @staticmethod
    def get_nft_by_ticker(ticker: str) -> NFT:
        if ticker not in NFT._instances:
            raise NotExistError("NFT", ticker)
        else:
            return NFT._instances[ticker]

    @staticmethod
    def get_nft(
        ticker: str,
        price_reference: str,
        price_reference_config: dict,
        base_currency: str,
    ) -> NFT:
        if ticker in NFT._instances:
            instance = NFT._instances[ticker]
            if (
                price_reference != instance.price_reference
                or price_reference_config != instance.price_reference_config
                or base_currency != instance.base_currency
            ):
                raise Exception("conflicting nft config")
        else:
            instance = NFT(
                ticker, price_reference, price_reference_config, base_currency
            )
            NFT._instances[ticker] = instance
        return instance

    def __init__(
        self,
        ticker: str,
        price_reference: str,
        price_reference_config: dict,
        base_currency: str,
    ):
        if ticker in NFT._instances:
            raise Exception(
                "please use NFT.get_nft or NFT.get_nft_by_ticker to get an instance"
            )
        self.ticker = ticker
        self.price_reference = price_reference
        self.price_reference_config = price_reference_config
        self.base_currency = base_currency

    @property
    async def floor_price(self) -> Decimal:
        if self.price_reference == "CoinGecko":
            return await coingecko_nft_price(self.price_reference_config["nft_id"])
        else:
            raise NotExistError("price_reference", self.price_reference)

    @property
    async def floor_price_in_usd(self) -> Decimal:
        if self.base_currency == "BTC":
            return await self.floor_price * await btc_price()
        elif self.base_currency == "ETH":
            return await self.floor_price * await eth_price()
        elif self.base_currency == "SOL":
            return await self.floor_price * await sol_price()
        else:
            raise NotExistError("base_currency", self.base_currency)

    async def get_balance(
        self, platform: str, asset_id: str, account: str | dict
    ) -> int:
        if isinstance(account, dict):
            ...
        elif platform == "Solana":
            ...
        elif platform == "Ordinal":
            bitcoin = Bitcoin()
            balance = await bitcoin.get_ordinal_balance(account, asset_id)
        else:
            evm_chain = EVM.get_chain(platform)
            nft = await evm_chain.get_nft(asset_id)
            balance = await nft.get_balance(account)
        return balance

    async def display_balance(self, balance: int) -> str:
        usd_value = balance * (await self.floor_price_in_usd)
        return display_nft(
            self.ticker, balance, self.base_currency, await self.floor_price, usd_value
        )
