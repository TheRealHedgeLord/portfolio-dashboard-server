from enum import StrEnum
from typing import Literal
from hashlib import sha256


class Color(StrEnum):
    BTC = "#F7931A"
    Bitcoin = "#F7931A"
    ETH = "#3E517A"
    Ethereum = "#3E517A"
    SOL = "#8E44AD"
    Solana = "#8E44AD"
    StableCoins = "#16A085"
    Gold = "#FFD700"
    NFT = "#FF69B4"
    MemeCoins = "#00FFA3"
    GMX = "#0057B7"
    LINK = "#1E90FF"

    @staticmethod
    def get_color(sector: str) -> str:
        if hasattr(Color, sector):
            return getattr(Color, sector)
        else:
            return f"#{sha256(sector.encode()).hexdigest()[0:6].upper()}"


def get_pie_chart_color(
    data: list[list],
) -> dict[Literal["slices"], dict[int, dict[Literal["color"], str]]]:
    return {
        "slices": {
            i: {"color": Color.get_color(data[i + 1][0])} for i in range(len(data) - 1)
        }
    }
