import os
import asyncio

from decimal import Decimal

from evm import EVM
from evm.constants import ADDRESSES, ABI
from dapps.curve import CurveClassicPool
from dapps.math import ClassicPool
from web2.coingecko import CoinGecko


class ConicDebtPool:
    debt_pool_address = "0xCFe7bA85D916875779F9668b606b70051901D5ca"
    curve_pool_address = "0x81db1af4cab88324d9391ef5d39eeb1eeae621d1"

    def __init__(self) -> None:
        self.ethereum = EVM.get_chain("Ethereum")
        self.contract = self.ethereum.get_contract(
            self.debt_pool_address, ABI["ConicDebtPool"]
        )
        self.coingecko = CoinGecko(os.environ["COINGECKO_API_KEY"])

    async def get_redeemable_tokens(
        self, debt_token_amount: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        raw_amount = int(debt_token_amount * Decimal(10**18))
        crv, cvx, cnc = await self.contract.view("redeemable", raw_amount)
        return (
            Decimal(crv) / Decimal(10**18),
            Decimal(cvx) / Decimal(10**18),
            Decimal(cnc) / Decimal(10**18),
        )

    async def get_token_prices(self) -> tuple[Decimal, Decimal, Decimal]:
        (crv_price, _), (cvx_price, _), (cnc_price, _) = (
            await self.coingecko.get_token_data(
                "curve-dao-token", "convex-finance", "conic-finance"
            )
        )
        return crv_price, cvx_price, cnc_price

    async def get_curve_pool_data(self) -> ClassicPool:
        cncDT = await self.ethereum.get_token(ADDRESSES[self.ethereum.name]["cncDT"])
        crvUSD = await self.ethereum.get_token(ADDRESSES[self.ethereum.name]["crvUSD"])
        curve_pool = await CurveClassicPool.get_pool(
            self.ethereum, self.curve_pool_address
        )
        return await curve_pool.get_reserve_data(cncDT, crvUSD)

    async def get_best_exit(self, account: str) -> dict:
        cncDT = await self.ethereum.get_token(ADDRESSES[self.ethereum.name]["cncDT"])
        balance = await cncDT.get_balance(account)
        (crv, cvx, cnc), (crv_price, cvx_price, cnc_price), curve_pool_data = (
            await asyncio.gather(
                self.get_redeemable_tokens(balance),
                self.get_token_prices(),
                self.get_curve_pool_data(),
            )
        )
        print(crv, cvx, cnc)
        market_price = curve_pool_data.market_price
        redemption_price = (
            crv * crv_price + cvx * cvx_price + cnc * cnc_price
        ) / balance
        if redemption_price >= market_price:
            swap_amount = Decimal("0")
            crvusd_amount_out = Decimal("0")
            redeem_amount = balance
        else:
            cncdt_diff, _ = curve_pool_data.liquidity_to_price(redemption_price)
            if cncdt_diff >= balance:
                swap_amount = balance
                redeem_amount = Decimal("0")
            else:
                swap_amount = cncdt_diff
                redeem_amount = balance - swap_amount
            crvusd_amount_out = curve_pool_data.get_amount_out(swap_amount)
        total_usd_value = crvusd_amount_out + redeem_amount * redemption_price
        return {
            "cncdt_balance": balance,
            "swap_amount": swap_amount,
            "redeem_amount": redeem_amount,
            "crvusd_amount_out": crvusd_amount_out,
            "redeemed_tokens": {
                "crv": {
                    "amount": crv * redeem_amount / balance,
                    "price": crv_price,
                    "usd_value": crv_price * crv * redeem_amount / balance,
                },
                "cvx": {
                    "amount": cvx * redeem_amount / balance,
                    "price": cvx_price,
                    "usd_value": cvx_price * cvx * redeem_amount / balance,
                },
                "cnc": {
                    "amount": cnc * redeem_amount / balance,
                    "price": cnc_price,
                    "usd_value": cnc_price * cnc * redeem_amount / balance,
                },
            },
            "total_usd_value": total_usd_value,
        }
