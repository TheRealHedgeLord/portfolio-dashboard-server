from math import log
from decimal import Decimal
from enum import StrEnum
from datetime import datetime

from exceptions import NotExistError

BITCOIN = "\u20BF"
ETHEREUM = "\u039E"
SOLANA = " SOL"


def _super_round_above_1(number: Decimal, decimals: int) -> str:
    integer = number // Decimal(10**decimals)
    fraction = str(number / Decimal(10**decimals) - integer)[2:5]
    return f"{integer}.{fraction}"


def display_decimal(number: Decimal) -> str:
    if number == Decimal("0"):
        return "0"
    decimals = log(number, 10)
    str_repr = str(number)
    if "E-" in str_repr:
        left, right = str_repr.split("E-")
        return "0.0{" + str(int(right) - 1) + "}" + left.replace(".", "")[0:6]
    elif decimals >= 12:
        return f"{_super_round_above_1(number, 12)}t"
    elif decimals >= 9:
        return f"{_super_round_above_1(number, 9)}b"
    elif decimals >= 6:
        return f"{_super_round_above_1(number, 6)}m"
    elif decimals >= 3:
        return f"{_super_round_above_1(number, 3)}k"
    elif decimals >= 0:
        return f"{_super_round_above_1(number, 0)}"
    elif decimals >= -3:
        return str(number)[0:8]
    else:
        return (
            "0.0{"
            + str(int(-decimals))
            + "}"
            + str(number)[2 - int(decimals) : 8 - int(decimals)]
        )


def display_btc_asset(ticker: str, btc_balance: Decimal, usd_value: Decimal) -> str:
    return f"{ticker}: {BITCOIN}{display_decimal(btc_balance)} (${display_decimal(usd_value)})"


def display_eth_asset(ticker: str, eth_balance: Decimal, usd_value: Decimal) -> str:
    return f"{ticker}: {ETHEREUM}{display_decimal(eth_balance)} (${display_decimal(usd_value)})"


def display_sol_asset(ticker: str, sol_balance: Decimal, usd_value: Decimal) -> str:
    return f"{ticker}: {display_decimal(sol_balance)}{SOLANA} (${display_decimal(usd_value)})"


def display_stable_coins(ticker: str, usd_value: Decimal) -> str:
    return f"{ticker}: ${display_decimal(usd_value)}"


def display_nft(
    ticker: str,
    balance: int,
    base_currency: str,
    floor_price: Decimal,
    usd_value: Decimal,
) -> str:
    if base_currency == "BTC":
        price_tag = f"{BITCOIN}{display_decimal(floor_price)}"
    elif base_currency == "ETH":
        price_tag = f"{ETHEREUM}{display_decimal(floor_price)}"
    elif base_currency == "SOL":
        price_tag = f"{display_decimal(floor_price)}{SOLANA}"
    else:
        raise NotExistError("base_currency", base_currency)
    return f"{ticker} ({price_tag}): {balance} (${display_decimal(usd_value)})"


def display_asset(
    ticker: str, token_balance: Decimal, token_price: Decimal, usd_value: Decimal
) -> str:
    return f"{ticker} (${display_decimal(token_price)}): {display_decimal(token_balance)} (${display_decimal(usd_value)})"


class Style(StrEnum):
    Purple = "\033[95m"
    Cyan = "\033[96m"
    DarkCyan = "\033[36m"
    Blue = "\033[94m"
    Green = "\033[92m"
    Yellow = "\033[93m"
    Red = "\033[91m"
    Bold = "\033[1m"
    UnderLine = "\033[4m"


def format_text(text: str, style: Style) -> str:
    return style + text + "\033[0m"


def pretty_report(raw_report: str) -> str:
    output = ""
    report = raw_report.replace("\t", " " * 8)
    lines = report.split("\n")
    width = max([len(line) for line in lines]) + 8
    separator = "|" + "-" * width + "|"
    output += separator
    for line in lines:
        if line == "":
            output += separator
        elif line[0] != " ":
            output += (
                "|" + format_text(line, Style.Bold) + " " * (width - len(line)) + "|"
            )
        else:
            output += "|" + line + " " * (width - len(line)) + "|"
    return output


def print_snapshot_report(
    timestamp: int, total_usd_value: Decimal, market_prices: dict, report: dict
) -> str:
    raw_report = f"Snapshot Time: {datetime.fromtimestamp(timestamp)}\n\n"
    raw_report += f"Total USD Value: ${round(total_usd_value, 2)}\n\n"
    raw_report += (
        f"Market Prices:\n"
        + "\n".join([f"\t{key}: ${market_prices[key]}" for key in market_prices])
        + "\n\n"
    )
    for module in report:
        raw_report += f"{module}\n"
        for item in report[module]:
            if isinstance(item, str):
                raw_report += f"\t{item}"
            elif isinstance(item, list):
                raw_report += f"\t{item[0]}:\n" + "\n".join(
                    [f"\t- {line}" for line in item[1::]]
                )
            raw_report += "\n"
        raw_report += "\n"
    return pretty_report(raw_report[0:-1])
