from typing import Literal, TypedDict

from dapps.gmx.gm import SupportedMarkets

SupportedGLV = Literal["GLV-BTC/USD", "GLV-ETH/USD"]


class GLVConfig(TypedDict):
    address: str
    gm_markets: list[SupportedMarkets]


GLV: dict[str, dict[SupportedGLV, GLVConfig]] = {
    "ArbitrumOne": {
        "GLV-BTC/USD": {
            "address": "0xdF03EEd325b82bC1d4Db8b49c30ecc9E05104b96",
            "gm_markets": ["GM-BTC/USD", "GM-STX/USD", "GM-ORDI/USD"],
        },
        "GLV-ETH/USD": {
            "address": "0x528A5bac7E746C9A509A1f4F6dF58A03d44279F9",
            "gm_markets": [
                "GM-ETH/USD",
                "GM-NEAR/USD",
                "GM-ATOM/USD",
                "GM-SHIB/USD",
                "GM-DOGE/USD",
                "GM-XRP/USD",
                "GM-LTC/USD",
            ],
        },
    }
}
