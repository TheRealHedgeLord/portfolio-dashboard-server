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
