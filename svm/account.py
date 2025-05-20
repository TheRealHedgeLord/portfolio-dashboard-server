import asyncio
import random

from solana.rpc.async_api import AsyncClient
from construct import Struct
from solders.pubkey import Pubkey  # type: ignore

from utils import CachedClass
from svm.layout import parse
from exceptions import NotExistError


class Account(metaclass=CachedClass):
    def __init__(self, rpc: AsyncClient, public_key: str, construct: Struct) -> None:
        self.rpc = rpc
        self.public_key = public_key
        self.construct = construct

    def __repr__(self) -> str:
        return f"<Account {self.public_key}>"

    async def get_data(self) -> dict:
        await asyncio.sleep(random.uniform(0, 3))
        response = await self.rpc.get_account_info(Pubkey.from_string(self.public_key))
        if response.value:
            return parse(response.value.data, self.construct)
        else:
            raise NotExistError("account", self.public_key)
