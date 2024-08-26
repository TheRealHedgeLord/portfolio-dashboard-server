import sqlite3

from pathlib import Path

from state.relational.table import Table
from state.relational.sql import Query
from utils import CachedClass


class RelationalDatabase(metaclass=CachedClass):
    path = f"{Path(__file__).parent}/.database.db"

    def __init__(self) -> None:
        self.connection = sqlite3.connect(self.path)
        self.cursor = self.connection.cursor()

    def get_all_tables(self) -> list[str]:
        self.cursor.execute("SELECT name FROM sqlite_master")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]

    def read(self, query: Query) -> Table:
        self.cursor.execute(query)
        columns = [row[0] for row in self.cursor.description]
        rows = self.cursor.fetchall()
        return Table(columns, rows)

    def write(self, *queries: Query) -> None:
        for query in queries:
            self.cursor.execute(query)
        self.connection.commit()
