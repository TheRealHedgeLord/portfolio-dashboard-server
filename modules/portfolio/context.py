from os import environ

from decimal import Decimal

from utils import GlobalContext
from web2.coingecko import CoinGecko
from dapps.lido import Lido
from dapps.jito import Jito
from dapps.makerdao import MakerDAO


_coingecko_client = CoinGecko(environ["COINGECKO_API_KEY"])
_lido = Lido()
_jito = Jito()
_maker = MakerDAO()


@GlobalContext.with_context
async def coingecko_price(token_id: str) -> Decimal:
    token_data = await _coingecko_client.get_token_data(token_id)
    price, _ = token_data[0]
    return price


@GlobalContext.with_context
async def coingecko_nft_price(nft_id: str) -> Decimal:
    return await _coingecko_client.get_nft_price(nft_id)


async def btc_price() -> Decimal:
    return await coingecko_price("bitcoin")


async def eth_price() -> Decimal:
    return await coingecko_price("ethereum")


async def sol_price() -> Decimal:
    return await coingecko_price("solana")


@GlobalContext.with_context
async def wsteth() -> Decimal:
    return await _lido.steth_per_wsteth()


@GlobalContext.with_context
async def jitosol() -> Decimal:
    return await _jito.sol_per_jitosol()


@GlobalContext.with_context
async def sdai() -> Decimal:
    return await _maker.dai_per_sdai()
