from typing import Protocol, TypedDict
from abc import abstractmethod
from decimal import Decimal


class Candle(TypedDict):
    timestamp: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class CEXInterface(Protocol):
    @abstractmethod
    async def get_token_balance(self, token_ticker: str) -> Decimal: ...

    @abstractmethod
    async def last_traded_price(self, ticker: str) -> Decimal: ...

    @abstractmethod
    async def get_candle_chart(
        self, ticker: str, interval: str, start_time: int, end_time: int
    ) -> list[Candle]: ...
