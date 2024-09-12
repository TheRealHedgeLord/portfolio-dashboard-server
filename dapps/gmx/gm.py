from typing import Literal, TypedDict

from evm.constants import ADDRESSES

SupportedMarkets = Literal[
    "GM-BTC/USD",
    "GM-ETH/USD",
    "GM-BTC",
    "GM-tBTC",
    "GM-ETH",
    "GM-wstETH/USDe",
    "GM-SOL/USD",
    "GM-LINK/USD",
    "GM-NEAR/USD",
    "GM-ATOM/USD",
    "GM-SHIB/USD",
    "GM-DOGE/USD",
    "GM-XRP/USD",
    "GM-LTC/USD",
    "GM-STX/USD",
    "GM-ORDI/USD",
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
        "GM-tBTC": {
            "market_prop": [
                "0xd62068697bCc92AF253225676D618B0C9f17C663",
                _BTC_INDEX,
                ADDRESSES["ArbitrumOne"]["tBTC"],
                ADDRESSES["ArbitrumOne"]["tBTC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 18,
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
        "GM-NEAR/USD": {
            "market_prop": [
                "0x63Dc80EE90F26363B3FCD609007CC9e14c8991BE",
                "0x1FF7F3EFBb9481Cbd7db4F932cBCD4467144237C",
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 6,
        },
        "GM-ATOM/USD": {
            "market_prop": [
                "0x248C35760068cE009a13076D573ed3497A47bCD4",
                "0x7D7F1765aCbaF847b9A1f7137FE8Ed4931FbfEbA",
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 6,
        },
        "GM-SHIB/USD": {
            "market_prop": [
                "0xB62369752D8Ad08392572db6d0cc872127888beD",
                "0x3E57D02f9d196873e55727382974b02EdebE6bfd",
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 6,
        },
        "GM-DOGE/USD": {
            "market_prop": [
                "0x6853EA96FF216fAb11D2d930CE3C508556A4bdc4",
                "0xC4da4c24fd591125c3F47b340b6f4f76111883d8",
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 6,
        },
        "GM-XRP/USD": {
            "market_prop": [
                "0x0CCB4fAa6f1F1B30911619f1184082aB4E25813c",
                "0xc14e065b0067dE91534e032868f5Ac6ecf2c6868",
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 6,
        },
        "GM-LTC/USD": {
            "market_prop": [
                "0xD9535bB5f58A1a75032416F2dFe7880C30575a41",
                "0xB46A094Bc4B0adBD801E14b9DB95e05E28962764",
                ADDRESSES["ArbitrumOne"]["WETH"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 18,
            "short_token_decimal": 6,
        },
        "GM-STX/USD": {
            "market_prop": [
                "0xD9377d9B9a2327C7778867203deeA73AB8a68b6B",
                "0xBaf07cF91D413C0aCB2b7444B9Bf13b4e03c9D71",
                ADDRESSES["ArbitrumOne"]["WBTC"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 8,
            "short_token_decimal": 6,
        },
        "GM-ORDI/USD": {
            "market_prop": [
                "0x93385F7C646A3048051914BDFaC25F4d620aeDF1",
                "0x1E15d08f3CA46853B692EE28AE9C7a0b88a9c994",
                ADDRESSES["ArbitrumOne"]["WBTC"],
                ADDRESSES["ArbitrumOne"]["USDC"],
            ],
            "long_token_decimal": 8,
            "short_token_decimal": 6,
        },
    }
}
