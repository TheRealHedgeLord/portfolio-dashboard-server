def _get_balances(
    market_snapshot: dict[str, tuple[float, float]],
    cash_percentage: float,
    index_value: float,
) -> dict[str, float]:
    total_mc = sum([market_snapshot[asset][1] for asset in market_snapshot])
    return {
        "cash": index_value * cash_percentage,
        **{
            asset: market_snapshot[asset][1]
            * (1 - cash_percentage)
            * index_value
            / total_mc
            for asset in market_snapshot
        },
    }


def build_index(
    market_prices: list[dict[str, tuple[float, float]]], cash_percentage: float
) -> list[float]:
    index_values = [1.0]
    balances = _get_balances(market_prices[0], cash_percentage, index_values[-1])
    for i in range(1, len(market_prices)):
        index_values.append(
            balances["cash"]
            + sum(
                [
                    balances["asset"]
                    * (market_prices[i][asset][0] if asset in market_prices[i] else 0)
                    for asset in balances
                    if asset != "cash"
                ]
            )
        )
        balances = _get_balances(market_prices[0], cash_percentage, index_values[-1])
    return index_values
