from decimal import Decimal


class ClassicPool:
    def __init__(self, reserve_base: Decimal, reserve_quote: Decimal) -> None:
        self.reserve_base = reserve_base
        self.reserve_quote = reserve_quote

    @property
    def k(self) -> Decimal:
        return self.reserve_base * self.reserve_quote

    @property
    def market_price(self) -> Decimal:
        return self.reserve_quote / self.reserve_base

    def reverse(self) -> None:
        _ = self.reserve_base
        self.reserve_base = self.reserve_quote
        self.reserve_quote = _

    def get_amount_out(self, amount_in: Decimal) -> Decimal:
        return self.reserve_quote - self.k / (self.reserve_base + amount_in)

    def get_amount_in(self, amount_out: Decimal) -> Decimal:
        return self.k / (self.reserve_quote - amount_out) - self.reserve_base

    def liquidity_to_price(self, target_price: Decimal) -> tuple[Decimal, Decimal]:
        delta_base = (self.k / target_price) ** Decimal("0.5") - self.reserve_base
        delta_quote = self.k / (self.reserve_base + delta_base) - self.reserve_quote
        return delta_base, delta_quote
