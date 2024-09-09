from utils import CachedClass
from state.api import APIGatewayClient
from state.boto import BotoClient
from state.table import Table
from state.sql import Query


class RDS(metaclass=CachedClass):
    def __init__(self, api_key: str | None = None) -> None:
        if api_key:
            self.client = APIGatewayClient(api_key)
        else:
            self.client = BotoClient()

    async def get_all_tables(self) -> list[str]:
        return await self.client.get_all_tables()

    async def read(self, query: Query) -> Table:
        columns, rows = await self.client.read(query)
        return Table(columns, rows)

    async def write(self, query: Query) -> None:
        await self.client.write(query)
