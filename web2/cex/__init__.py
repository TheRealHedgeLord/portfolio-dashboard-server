from typing import Protocol
from decimal import Decimal
from abc import abstractmethod

from web2.cex.binance import Binance

EXCHANGES = {"binance": Binance}


class CEXInterface(Protocol):
    @abstractmethod
    async def get_token_balance(self, token_ticker: str) -> Decimal: ...

    @abstractmethod
    async def last_traded_price(self, ticker: str) -> Decimal: ...


def get_cex(exchange: str, auth: dict) -> CEXInterface:
    return EXCHANGES[exchange](**auth)
