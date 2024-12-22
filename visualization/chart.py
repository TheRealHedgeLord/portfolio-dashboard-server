import os
import json
import uuid
import webbrowser

from typing import Literal

from visualization.src import CHART_FUNCTION_SRC, CHART_DIV_SRC
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
    ) -> None:
        self.chart_id = uuid.uuid4().hex
        self.chart_type = chart_type
        self.title = title
        self.data = json.dumps(data)
        self.height = height
        self.options = ", ".join(
            [f"{snake_to_camel(key)}: {json.dumps(options[key])}" for key in options]
        )

    @property
    def chart_function(self) -> str:
        return insert(
            CHART_FUNCTION_SRC,
            chart_id=self.chart_id,
            data=self.data,
            title=self.title,
            chart_type=self.chart_type,
            options=self.options,
        )

    @property
    def chart_div(self) -> str:
        return insert(CHART_DIV_SRC, chart_id=self.chart_id, height=self.height)
