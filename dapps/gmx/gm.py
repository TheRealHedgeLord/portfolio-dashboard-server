from typing import Literal, TypedDict

from evm.constants import ADDRESSES

SupportedMarkets = Literal[
    "GM-BTC/USD",
    "GM-ETH/USD",
    "GM-BTC",
    "GM-ETH",
    "GM-wstETH/USDe",
    "GM-SOL/USD",
    "GM-LINK/USD",
]

_BTC_INDEX = "0x47904963fc8b2340414262125aF798B9655E58Cd"


class GMMarket(TypedDict):
    market_prop: list[str]
    long_token_decimal: int
    short_token_decimal: int


MARKETS: dict[str, dict[SupportedMarkets, GMMarket]] = {
    "ArbitrumOne": {
        "GM-BTC/USD": {
            "market_prop": [
                "0x47c031236e19d024b42f8AE6780E44A573170703",
                _BTC_INDEX,
                ADDRESSES["ArbitrumOne"]["WBTC"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 8,
            "short_token_decimal": 6,
        },
        "GM-ETH/USD": {
            "market_prop": [
                "0x70d95587d40A2caf56bd97485aB3Eec10Bee6336",
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 6,
        },
        "GM-BTC": {
            "market_prop": [
                "0x7C11F78Ce78768518D743E81Fdfa2F860C6b9A77",
                _BTC_INDEX,
                ADDRESSES["ArbitrumOne"]["WBTC"],
                ADDRESSES["ArbitrumOne"]["WBTC"],
            ],
            "long_token_decimal": 8,
            "short_token_decimal": 8,
        },
        "GM-ETH": {
            "market_prop": [
                "0x450bb6774Dd8a756274E0ab4107953259d2ac541",
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["WETH"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 18,
        },
        "GM-SOL/USD": {
            "market_prop": [
                "0x09400D9DB990D5ed3f35D7be61DfAEB900Af03C9",
                ADDRESSES["ArbitrumOne"]["WSOL"],
                ADDRESSES["ArbitrumOne"]["WSOL"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 9,
            "short_token_decimal": 6,
        },
        "GM-LINK/USD": {
            "market_prop": [
                "0x7f1fa204bb700853D36994DA19F830b6Ad18455C",
                ADDRESSES["ArbitrumOne"]["LINK"],
                ADDRESSES["ArbitrumOne"]["LINK"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 6,
        },
    }
}
