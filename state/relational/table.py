import json

from os import environ
from functools import cached_property, cache
from typing import Literal, Any
from copy import deepcopy

from state.relational.types import from_sqlite, ValueType

_MAX_COLUMN_WIDTH = (
    int(environ["MAX_COLUMN_WIDTH"]) if "MAX_COLUMN_WIDTH" in environ else 32
)
_MAX_ROW_NUM = int(environ["MAX_ROW_NUM"]) if "MAX_ROW_NUM" in environ else 8


def _value_repr(value: Any) -> str:
    if isinstance(value, dict) or isinstance(value, list):
        return json.dumps(value)
    else:
        return str(value)


def _display_value(value: Any, width: int) -> str:
    value_repr = _value_repr(value)
    if len(value_repr) + 2 > width:
        return " " + value_repr[0 : width - 6] + " ... "
    else:
        return " " + value_repr + " " * (width - len(value_repr) - 2) + " "


class Table:
    def __init__(self, columns: list[str], rows: list[tuple]) -> None:
        self._columns = columns
        self._rows = [[from_sqlite(value) for value in row] for row in rows]

    @cached_property
    def _displayed_rows(self) -> list[list[ValueType | None]]:
        if self.row_count <= _MAX_ROW_NUM:
            return [[i] + self.rows[i] for i in range(self.row_count)]
        else:
            return [
                [i] + self.rows[i]
                for i in [0, 1] + [self.row_count - 6 + j for j in range(6)]
            ]

    @cached_property
    def _column_widths(self) -> list[int]:
        column_widths = [min(len(str(self.row_count)) + 2, _MAX_COLUMN_WIDTH)]
        for i in range(self.column_count):
            column_head_width = len(self.columns[i])
            value_widths = [
                len(_value_repr(row[i + 1])) for row in self._displayed_rows
            ]
            max_content_width = max([column_head_width] + value_widths) + 2
            column_widths.append(min(max_content_width, _MAX_COLUMN_WIDTH))
        return column_widths

    @cached_property
    def _sep(self) -> str:
        return "|" + "|".join(["-" * width for width in self._column_widths]) + "|\n"

    @cached_property
    def _head(self) -> str:
        head = "|" + " " * self._column_widths[0] + "|"
        for i in range(len(self.columns)):
            head += _display_value(self.columns[i], self._column_widths[i + 1]) + "|"
        return head + "\n"

    @cache
    def _display_row(self, displayed_row_index: int) -> str:
        displayed_row = self._displayed_rows[displayed_row_index]
        return (
            "|"
            + "|".join(
                [
                    _display_value(displayed_row[i], self._column_widths[i])
                    for i in range(len(displayed_row))
                ]
            )
            + "|\n"
        )

    @cached_property
    def _rows_repr(self) -> str:
        if self.row_count <= _MAX_ROW_NUM:
            return "".join(
                [self._display_row(i) for i in range(len(self._displayed_rows))]
            )
        else:
            return (
                self._display_row(0)
                + self._display_row(1)
                + "...\n"
                + "".join([self._display_row(i) for i in range(2, _MAX_ROW_NUM)])
            )

    @cache
    def __repr__(self) -> str:
        return self._sep + self._head + self._sep + self._rows_repr + self._sep

    @property
    def columns(self) -> list[str]:
        return self._columns.copy()

    @property
    def rows(self) -> list[list[ValueType | None]]:
        return deepcopy(self._rows)

    @cached_property
    def row_count(self) -> int:
        return len(self.rows)

    @cached_property
    def column_count(self) -> int:
        return len(self.columns)

    @cache
    def get_column(self, column_name: str) -> list[ValueType | None]:
        index = self.columns.index(column_name)
        return [row[index] for row in self.rows]

    @cache
    def get_rows(
        self, rows: int | tuple[int, int] | Literal["all"] = "all"
    ) -> list[dict[str, ValueType | None]]:
        if isinstance(rows, int):
            target_rows = self.rows[rows : rows + 1]
        elif isinstance(rows, tuple):
            target_rows = self.rows[rows[0] : rows[1]]
        elif rows == "all":
            target_rows = self.rows
        return [
            {self.columns[i]: row[i] for i in range(len(self.columns))}
            for row in target_rows
        ]
