from state.relational import RelationalDatabase
from state.relational.sql import Query
from cli.state_manager.serializers import from_cli_arg

_relational_database = RelationalDatabase()


async def get_all_tables() -> None:
    tables = _relational_database.get_all_tables()
    print(", ".join(tables))


async def get_table(table_name: str, cli_kwargs: str) -> None:
    kwargs = from_cli_arg(cli_kwargs)
    table = _relational_database.read(Query.get_table(table_name, **kwargs))  # type: ignore
    print(table.parsed)


async def insert_row(table_name: str, cli_column_values: str) -> None:
    column_values = from_cli_arg(cli_column_values)
    _relational_database.write(Query.insert_row(table_name, column_values))  # type: ignore


async def delete_rows(table_name: str, cli_match_values: str | None = None) -> None:
    match_values = from_cli_arg(cli_match_values) if cli_match_values else None
    _relational_database.write(Query.delete_rows(table_name, match_values=match_values))  # type: ignore


async def create_table(table_name: str, cli_column_types: str) -> None:
    column_types = from_cli_arg(cli_column_types)
    _relational_database.write(Query.create_table(table_name, column_types))  # type: ignore


async def delete_table(table_name: str) -> None:
    _relational_database.write(Query.delete_table(table_name))


async def update_table(
    table_name: str, cli_match_values: str, cli_new_values: str
) -> None:
    match_values = from_cli_arg(cli_match_values)
    new_values = from_cli_arg(cli_new_values)
    _relational_database.write(Query.update_table(table_name, match_values, new_values))  # type: ignore


methods = {
    "get_all_tables": get_all_tables,
    "get_table": get_table,
    "insert_row": insert_row,
    "delete_rows": delete_rows,
    "create_table": create_table,
    "delete_table": delete_table,
    "update_table": update_table,
}
