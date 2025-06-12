from decimal import Decimal

from evm import EVM
from evm.constants import ABI, ADDRESSES


async def get_rlp_price() -> Decimal:
    ethereum = EVM.get_chain("Ethereum")
    oracle = ethereum.get_contract(
        ADDRESSES[ethereum.name]["RLPPriceOracle"], ABI["RLPPriceOracle"]
    )
    price, _ = await oracle.view("lastPrice")
    return Decimal(price) / Decimal(10**18)
