import hashlib

from typing import Any

from web3 import AsyncWeb3
from eth_typing.evm import ChecksumAddress

from state.relational import RelationalDatabase
from state.relational.sql import Query
from utils import CachedClass

_CACHE_TABLE_NAME = "_cache"

_cache_database = RelationalDatabase()

if _CACHE_TABLE_NAME not in _cache_database.get_all_tables():
    _cache_database.write(
        Query.create_table(_CACHE_TABLE_NAME, {"key": "string", "value": "json"})
    )


def _read_from_cache(key: str) -> Any:
    table = _cache_database.read(
        Query.get_table(_CACHE_TABLE_NAME, columns=["value"], match_values={"key": key})
    )
    if table.row_count > 0:
        value = table.get_column("value")[0]
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        else:
            return value


def _write_to_cache(key: str, value: Any) -> None:
    if isinstance(value, list) or isinstance(value, tuple):
        json_value = list(value)
    else:
        json_value = [value]
    _cache_database.write(
        Query.insert_row(_CACHE_TABLE_NAME, {"key": key, "value": json_value})
    )


class Contract(metaclass=CachedClass):
    def __init__(
        self, network_id: int, rpc: AsyncWeb3, address: ChecksumAddress, abi: list
    ) -> None:
        self.network_id = network_id
        self.rpc = rpc
        self.address = address
        self.contract = rpc.eth.contract(address, abi=abi)

    def __repr__(self) -> str:
        return f"<Contract({self.address}) network_id: {self.network_id}>"

    def _get_cache_key(self, method: str, *args: Any) -> str:
        call_repr = f"{self.network_id}{self.address.lower()}{method}{args}".encode()
        return hashlib.sha256(call_repr).hexdigest()

    async def _view(self, method, *args) -> Any:
        return await getattr(self.contract.functions, method)(*args).call()

    async def view(
        self, method, *args, immutable: bool = False, override: bool = False
    ) -> Any:
        if not immutable:
            return await self._view(method, *args)
        else:
            key = self._get_cache_key(method, *args)
            if override:
                value = await self._view(method, *args)
                _write_to_cache(key, value)
                return value
            else:
                value_from_cache = _read_from_cache(key)
                if value_from_cache == None:
                    value = await self._view(method, *args)
                    _write_to_cache(key, value)
                    return value
                else:
                    return value_from_cache
