from decimal import Decimal


def create_index(weight: Decimal, prices: list[Decimal]) -> list[Decimal]:
    k = (Decimal("1") - weight) ** 2 / prices[0]
    return [Decimal("2") * (p * k) ** Decimal("0.5") for p in prices]

    # index = [Decimal("1")]
    # balance_principal = index[0] * weight / prices[0]
    # for i in range(1, len(prices)):
    #     diff = (prices[i] - prices[i - 1]) * balance_principal
    #     index.append(index[-1] + diff)
    #     balance_principal = index[-1] * weight / prices[-1]
    # return index
