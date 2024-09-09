from __future__ import annotations

from typing import Literal
from typing_extensions import Self

from state.serializers import serialize, StateDataType, ColumnType


class Query(str):
    def __new__(cls, sql: str) -> Self:
        return super().__new__(cls, sql)

    @staticmethod
    def _get_statement(
        statement: Literal["WHERE", "SET"],
        key_value_pairs: dict[str, StateDataType] | None,
    ) -> str:
        return (
            (
                f" {statement} "
                + " AND ".join(
                    [
                        f"{column} = {serialize(key_value_pairs[column])}"
                        for column in key_value_pairs
                    ]
                )
            )
            if key_value_pairs
            else ""
        )

    @staticmethod
    def create_table(table_name: str, column_types: dict[str, ColumnType]) -> Query:
        columns = ", ".join(
            [f"{column} {column_types[column]}" for column in column_types]
        )
        query = f"CREATE TABLE {table_name} ({columns})"
        return Query(query)

    @staticmethod
    def insert_row(table_name: str, column_values: dict[str, StateDataType]) -> Query:
        columns = []
        values = []
        for column in column_values:
            columns.append(column)
            values.append(serialize(column_values[column]))
        return Query(
            "INSERT INTO {} ({}) VALUES ({})".format(
                table_name, ", ".join(columns), ", ".join(values)
            )
        )

    @staticmethod
    def insert_rows(
        table_name: str, columns: list[str], rows: list[list[StateDataType]]
    ) -> Query:
        return Query(
            "INSERT INTO {} ({}) VALUES {}".format(
                table_name,
                ", ".join(columns),
                ", ".join(
                    [
                        "({})".format(", ".join([serialize(value) for value in row]))
                        for row in rows
                    ]
                ),
            )
        )

    @staticmethod
    def update_table(
        table_name: str,
        match_values: dict[str, StateDataType],
        new_values: dict[str, StateDataType],
    ) -> Query:
        set_statement = Query._get_statement("SET", new_values)
        where_statement = Query._get_statement("WHERE", match_values)
        return Query(f"UPDATE {table_name}{set_statement}{where_statement}")

    @staticmethod
    def delete_table(table_name: str) -> Query:
        return Query(f"DROP TABLE {table_name}")

    @staticmethod
    def truncate_table(table_name: str) -> Query:
        return Query(f"DELETE FROM {table_name}")

    @staticmethod
    def get_table(
        table_name: str,
        columns: list[str] | Literal["*"] = "*",
        match_values: dict[str, StateDataType] | None = None,
    ) -> Query:
        column_statement = ", ".join(columns)
        where_statement = Query._get_statement("WHERE", match_values)
        return Query(f"SELECT {column_statement} FROM {table_name}{where_statement}")

    @staticmethod
    def delete_rows(
        table_name: str, match_values: dict[str, StateDataType] | None = None
    ) -> Query:
        where_statement = Query._get_statement("WHERE", match_values)
        return Query(f"DELETE FROM {table_name}{where_statement}")
