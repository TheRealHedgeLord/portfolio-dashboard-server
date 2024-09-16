import os
import json
import webbrowser

from typing import Literal

from visualization.src import GOOGLE_CHART_HTML
from visualization.htmlutils import insert
from utils import snake_to_camel


DEFAULT_CACHE_DIR = os.environ.get("DEFAULT_CACHE_DIR")


class Chart:
    def __init__(
        self,
        chart_type: Literal["LineChart", "AreaChart", "PieChart"],
        title: str,
        data: list[list],
        height: str = "500",
        options: dict = {},
        cache_root: str | None = DEFAULT_CACHE_DIR,
    ):
        self.chart_type = chart_type
        self.title = title
        self.data = data
        self.height = height
        self.cache_root = cache_root if cache_root else "./"
        self.options = ", ".join(
            [f"{snake_to_camel(key)}: {json.dumps(options[key])}" for key in options]
        )

    @property
    def html(self) -> str:
        return insert(
            GOOGLE_CHART_HTML,
            data=self.data,
            title=self.title,
            chart_type=self.chart_type,
            height=self.height,
            options=self.options,
        )

    @property
    def cache_file_path(self) -> str:
        return f"{self.cache_root}cache.html"

    def draw(self) -> None:
        with open(self.cache_file_path, mode="w") as f:
            f.write(self.html)
        webbrowser.open(f"file://{os.path.realpath(self.cache_file_path)}")
