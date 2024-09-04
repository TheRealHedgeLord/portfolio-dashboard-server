from state.relational import RelationalDatabase
from state.relational.sql import Query


async def get_next_page(uuid: str) -> str:
    table_name = "pagination"
    database = RelationalDatabase()
    content = database.read(
        Query.get_table(table_name, match_values={"uuid": uuid})
    ).get_column("content")[0]
    database.write(Query.delete_rows(table_name, match_values={"uuid": uuid}))
    return content  # type: ignore


methods = {"get_next_page": get_next_page}
