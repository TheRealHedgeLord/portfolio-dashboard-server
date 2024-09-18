import os
import webbrowser

from typing import Literal

from visualization.src import CANVAS_SRC
from visualization.htmlutils import insert
from visualization.chart import Chart


DEFAULT_CACHE_DIR = os.environ.get("DEFAULT_CACHE_DIR")


class Canvas:
    charts: list[Chart]

    def __init__(self, cache_root: str | None = DEFAULT_CACHE_DIR) -> None:
        self.cache_root = cache_root if cache_root else "./"
        self.charts = []

    def add_chart(
        self,
        chart_type: Literal["LineChart", "AreaChart", "PieChart"],
        title: str,
        data: list[list],
        height: str = "500",
        options: dict = {},
    ) -> None:
        self.charts.append(
            Chart(chart_type, title, data, height=height, options=options)
        )

    @property
    def _chart_functions(self) -> str:
        return "\n".join([chart.chart_function for chart in self.charts])

    @property
    def _chart_divs(self) -> str:
        return "\n".join([chart.chart_div for chart in self.charts])

    @property
    def html(self) -> str:
        return insert(
            CANVAS_SRC, chart_function=self._chart_functions, chart_div=self._chart_divs
        )

    @property
    def cache_file_path(self) -> str:
        return f"{self.cache_root}cache.html"

    def draw(self) -> None:
        with open(self.cache_file_path, mode="w") as f:
            f.write(self.html)
        webbrowser.open(f"file://{os.path.realpath(self.cache_file_path)}")
