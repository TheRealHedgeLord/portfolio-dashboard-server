from web2.cex.types import CEXInterface
from web2.cex.binance import Binance

EXCHANGES = {"binance": Binance}


def get_cex(exchange: str, auth: dict) -> CEXInterface:
    return EXCHANGES[exchange](**auth)
