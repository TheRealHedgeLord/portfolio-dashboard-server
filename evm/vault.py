import time

from os import environ
from typing import TypedDict, Literal
from decimal import Decimal
from eth_account import Account
from web3 import Web3, AsyncWeb3
from eth_utils.address import to_checksum_address
from eth_typing import ChecksumAddress
from eth_abi import abi

from utils import CachedClass
from evm.constants import ABI, ZERO_ADDRESS
from evm.contract import Contract
from evm.erc20 import ERC20


class Signature(TypedDict):
    v: int
    r: str
    s: str


def _get_bytes_32(number: int) -> str:
    hex_no_prefix = hex(number)[2::]
    return "0x" + "0" * (64 - len(hex_no_prefix)) + hex_no_prefix


class Vault(metaclass=CachedClass):
    def __init__(
        self,
        network_id: int,
        rpc: AsyncWeb3,
        address: ChecksumAddress,
        signer_private_key: str | None = None,
    ) -> None:
        self.web3 = Web3()
        self.rpc = rpc
        self.address = address
        self.network_id = network_id
        self.signer = (
            Account.from_key(signer_private_key)
            if signer_private_key
            else Account.from_key(environ["TEST_KEY"])
        )
        self.contract = Contract(network_id, rpc, address, ABI["Vault"])

    async def _sign(
        self, token: str, to: str, amount: int, seconds_to_expiry: int
    ) -> tuple[str, str, int, int, Signature]:
        nonce = await self.contract.view("nonce")
        expiry = int(time.time() + seconds_to_expiry)
        message_hash = self.web3.keccak(
            abi.encode(
                (
                    "uint256",
                    "address",
                    "uint256",
                    "address",
                    "address",
                    "uint256",
                    "uint256",
                ),
                [self.network_id, self.address, nonce, token, to, amount, expiry],
            )
        )
        signature = self.signer.signHash(message_hash)
        return (
            token,
            to,
            amount,
            expiry,
            {
                "v": signature.v,
                "r": _get_bytes_32(signature.r),
                "s": _get_bytes_32(signature.s),
            },
        )

    async def sign_withdrawal(
        self,
        to: str,
        token_address: str = ZERO_ADDRESS,
        amount: Decimal | None = None,
        seconds_to_expiry: int = 300,
    ) -> tuple[str, str, int, int, Signature]:
        if token_address == ZERO_ADDRESS:
            if not amount:
                raw_amount = int(await self.rpc.eth.get_balance(self.address))
            else:
                raw_amount = int(amount * Decimal(10**18))
        else:
            token = ERC20(self.network_id, self.rpc, to_checksum_address(token_address))
            await token.initialize()
            if not amount:
                raw_amount = int(
                    (await token.get_balance(self.address))
                    * Decimal(10**token.decimals)
                )
            else:
                raw_amount = int(amount * Decimal(10**token.decimals))
        return await self._sign(token_address, to, raw_amount, seconds_to_expiry)
