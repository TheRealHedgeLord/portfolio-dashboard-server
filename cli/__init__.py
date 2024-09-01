from uuid import uuid4
from os import environ

from cli import (
    gm_price_tracker,
    token_price_tracker,
    state_manager,
    portfolio,
    scroll_marks,
    pagination,
)
from state.relational import RelationalDatabase
from state.relational.sql import Query


_PAGINATION_TABLE = "pagination"
_database = RelationalDatabase()
if _PAGINATION_TABLE not in _database.get_all_tables():
    _database.write(
        Query.create_table(_PAGINATION_TABLE, {"uuid": "string", "content": "string"})
    )


PAGE_SIZE = int(environ["PAGE_SIZE"])


options = {
    "gm_price_tracker": gm_price_tracker.methods,
    "token_price_tracker": token_price_tracker.methods,
    "state_manager": state_manager.methods,
    "portfolio": portfolio.methods,
    "scroll_marks": scroll_marks.methods,
    "pagination": pagination.methods,
}


async def run_command(option: str, method: str, *args: str) -> None:
    result = await options[option][method](*args)
    if isinstance(result, str):
        if len(result) > PAGE_SIZE:
            uuid = uuid4().hex
            current_page = result[0:PAGE_SIZE]
            remaining_content = result[PAGE_SIZE::]
            _database.write(
                Query.insert_row(
                    _PAGINATION_TABLE, {"uuid": uuid, "content": remaining_content}
                )
            )
            print(uuid + current_page)
        else:
            print("0" * 32 + result)
