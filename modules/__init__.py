import inspect

from typing import Callable

from modules.portfolio import PortfolioModule
from modules.scroll import ScrollMarksTracker
from modules.linea import LineaPointsTracker
from modules.gmx import GMXPerformanceTracker

MODULES = {
    "portfolio": PortfolioModule,
    "scroll": ScrollMarksTracker,
    "linea": LineaPointsTracker,
    "gmx": GMXPerformanceTracker,
}


def _get_method_annotation(method: Callable) -> str:
    args = inspect.getargs(method.__code__).args
    return "{}({})".format(
        method.__name__, ", ".join([arg for arg in args if arg != "self"])
    )


def help() -> None:
    for module in MODULES:
        print(f"\033[1m{module}\033[0m")
        for name in dir(MODULES[module]):
            if name[0] != "_":
                method = getattr(MODULES[module], name)
                if hasattr(method, "__code__") and hasattr(method, "__name__"):
                    print(f"\t{_get_method_annotation(method)}")
