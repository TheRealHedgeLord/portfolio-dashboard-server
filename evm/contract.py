import hashlib

from typing import Any

from web3 import AsyncWeb3
from eth_typing.evm import ChecksumAddress

from utils import CachedClass


class Contract(metaclass=CachedClass):
    def __init__(
        self, network_id: int, rpc: AsyncWeb3, address: ChecksumAddress, abi: list
    ) -> None:
        self.network_id = network_id
        self.rpc = rpc
        self.address = address
        self.contract = rpc.eth.contract(address, abi=abi)
        self._cache = {}

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
                self._cache[key] = value
                return value
            else:
                value_from_cache = self._cache.get(key)
                if value_from_cache == None:
                    value = await self._view(method, *args)
                    self._cache[key] = value
                    return value
                else:
                    return value_from_cache
