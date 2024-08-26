import asyncio

from decimal import Decimal
from functools import cache, cached_property

from solders.pubkey import Pubkey  # type: ignore
from solana.rpc.async_api import AsyncClient

from utils import CachedClass, InitializableClass, initialized_property
from svm.account import Account
from svm.constants import (
    TOKEN_PROGRAM_ID,
    ASSOCIATED_TOKEN_PROGRAM_ID,
    TOKEN_METADATA_PROGRAM_ID,
)
from svm.layout.spl import TokenAccount, TokenMint, TokenMetadata
from exceptions import NotExistError


class SPLToken(InitializableClass, metaclass=CachedClass):
    def __init__(self, rpc: AsyncClient, mint: str) -> None:
        self.rpc = rpc
        self.mint = mint
        self.mint_account = Account(rpc, mint, TokenMint)
        self.metadata_account = Account(rpc, self.token_metadata_account, TokenMetadata)

    def __repr__(self) -> str:
        return f"<SPLToken {self.mint}>"

    async def _get_mint_account_data(self) -> dict:
        mint_account_data = await self.mint_account.get_data()
        if mint_account_data:
            return mint_account_data
        else:
            raise NotExistError("TokenMint", self.mint)

    async def _intialize_decimals(self) -> None:
        if not hasattr(self, "_decimals"):
            mint_account_data = await self._get_mint_account_data()
            self._decimals = mint_account_data["decimals"]

    async def _intialize_metadata(self) -> None:
        if not hasattr(self, "_symbol") or not hasattr(self, "_name"):
            metadata = await self._get_token_metadata()
            self._symbol = metadata["data"]["symbol"]
            self._name = metadata["data"]["name"]

    async def _get_token_metadata(self) -> dict:
        token_metadata = await self.metadata_account.get_data()
        if token_metadata:
            return token_metadata
        else:
            raise NotExistError("TokenMetadata", self.token_metadata_account)

    async def _initialize(self) -> None:
        await asyncio.gather(self._intialize_decimals(), self._intialize_metadata())

    @property
    @initialized_property("_decimals")
    def decimals(self) -> Decimal: ...

    @property
    @initialized_property("_symbol")
    def symbol(self) -> str: ...

    @property
    @initialized_property("_name")
    def name(self) -> str: ...

    @cache
    def get_associated_token_account(self, owner: str) -> str:
        key, _ = Pubkey.find_program_address(
            seeds=[
                bytes(Pubkey.from_string(owner)),
                bytes(Pubkey.from_string(TOKEN_PROGRAM_ID)),
                bytes(Pubkey.from_string(self.mint)),
            ],
            program_id=Pubkey.from_string(ASSOCIATED_TOKEN_PROGRAM_ID),
        )
        return str(key)

    @cached_property
    def token_metadata_account(self) -> str:
        key, _ = Pubkey.find_program_address(
            seeds=[
                b"metadata",
                bytes(Pubkey.from_string(TOKEN_METADATA_PROGRAM_ID)),
                bytes(Pubkey.from_string(self.mint)),
            ],
            program_id=Pubkey.from_string(TOKEN_METADATA_PROGRAM_ID),
        )
        return str(key)

    async def get_supply(self) -> Decimal:
        return (await self._get_mint_account_data())["supply"]

    async def get_balance(self, account: str) -> Decimal:
        associated_token_account = Account(
            self.rpc, self.get_associated_token_account(account), TokenAccount
        )
        token_account_data = await associated_token_account.get_data()
        if token_account_data:
            return Decimal(token_account_data["amount"]) / Decimal(10**self.decimals)
        else:
            return Decimal("0")
