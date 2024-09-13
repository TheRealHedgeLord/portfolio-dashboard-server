from decimal import Decimal

from dapps.gmx.gm import SupportedMarkets
from dapps.gmx.glv import SupportedGLV


ALL_TRACKED_CHAINS = ["ArbitrumOne"]

ALL_TRACKED_GM: dict[str, list[SupportedMarkets]] = {
    "ArbitrumOne": list(SupportedMarkets.__args__)
}

ALL_TRACKED_GLV: dict[str, list[SupportedGLV]] = {
    "ArbitrumOne": list(SupportedGLV.__args__)
}
