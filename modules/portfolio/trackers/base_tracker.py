from abc import abstractmethod
from decimal import Decimal

from state import RDS
from state.sql import Query
from state.serializers import ColumnType
from modules.portfolio.account import AccountCipher


class BaseTracker:
    config_table_name: str
    config_table_schema: dict[str, ColumnType]

    def __init__(self, state: RDS, passphrase: str) -> None:
        self.cipher = AccountCipher(passphrase)
        self.state = state

    async def initialize(self) -> None:
        self.config = await self.state.read(Query.get_table(self.config_table_name))

    @abstractmethod
    async def get_snapshot(self) -> tuple[Decimal, dict, dict, dict]: ...
