from state.relational import RelationalDatabase
from state.relational.sql import Query

_relational_database = RelationalDatabase()


async def show_all_tables() -> None:
    tables = _relational_database.get_all_tables()
    print(", ".join(tables))


async def show_table(table_name: str) -> None:
    table = _relational_database.read(Query.get_table(table_name))
    print(table_name)
    print(table)


methods = {"show_all_tables": show_all_tables, "show_table": show_table}
