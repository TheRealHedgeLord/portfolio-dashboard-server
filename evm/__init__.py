from __future__ import annotations

from decimal import Decimal

from web3 import AsyncWeb3
from eth_utils.address import to_checksum_address

from evm.chains import get_chain_meta
from evm.contract import Contract
from evm.erc20 import ERC20
from evm.nft import ERC721
from evm.vault import Vault
from utils import CachedClass


class EVM(metaclass=CachedClass):
    @staticmethod
    def get_chain(name: str) -> EVM:
        network_id, rpc_url, symbol = get_chain_meta(name)
        return EVM(name, network_id, rpc_url, symbol)

    def __init__(self, name: str, network_id: int, rpc_url: str, symbol: str) -> None:
        self.name = name
        self.network_id = network_id
        self.symbol = symbol
        self.rpc = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(rpc_url))

    def __repr__(self) -> str:
        return f"<EVM network_id: {self.network_id}>"

    async def get_balance(self, address: str) -> Decimal:
        wei = await self.rpc.eth.get_balance(to_checksum_address(address))
        return Decimal(wei) / Decimal(10**18)

    def get_contract(self, address: str, abi: list) -> Contract:
        return Contract(self.network_id, self.rpc, to_checksum_address(address), abi)

    async def get_token(self, token_address: str) -> ERC20:
        token = ERC20(self.network_id, self.rpc, to_checksum_address(token_address))
        await token.initialize()
        return token

    async def get_nft(self, nft_address: str) -> ERC721:
        nft = ERC721(self.network_id, self.rpc, to_checksum_address(nft_address))
        await nft.initialize()
        return nft

    def get_vault(
        self, valut_address: str, signer_private_key: str | None = None
    ) -> Vault:
        return Vault(
            self.network_id,
            self.rpc,
            to_checksum_address(valut_address),
            signer_private_key=signer_private_key,
        )
