import asyncio
import random
from decimal import Decimal

from solana.rpc.async_api import AsyncClient
from construct import Struct
from solders.pubkey import Pubkey  # type: ignore

from utils import CachedClass
from svm.account import Account
from svm.token import SPLToken
from svm.constants import SOLANA_HTTP_RPC_URL
from exceptions import InvalidURL


class SVM(metaclass=CachedClass):
    def __init__(self, rpc_url: str = SOLANA_HTTP_RPC_URL) -> None:
        if "://" not in rpc_url:
            raise InvalidURL()
        self.rpc = AsyncClient(rpc_url)

    def __repr__(self) -> str:
        protocol, uri = self.rpc._provider.endpoint_uri.split("://")
        endpoints = uri.split("/")
        return f"<SVM {protocol}://{endpoints[0]}>"

    def get_account(self, public_key: str, construct: Struct) -> Account:
        return Account(self.rpc, public_key, construct)

    async def get_token(self, mint: str) -> SPLToken:
        token = SPLToken(self.rpc, mint)
        await token.initialize()
        return token

    async def get_balance(self, account: str) -> Decimal:
        await asyncio.sleep(random.uniform(0, 3))
        response = await self.rpc.get_balance(Pubkey.from_string(account))
        return Decimal(response.value) / Decimal(10**9)
