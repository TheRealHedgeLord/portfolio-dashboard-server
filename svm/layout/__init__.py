from typing import Any
from construct import Bytes, Struct, Container, ListContainer
from solders.pubkey import Pubkey  # type: ignore


PublicKey = Bytes(32)


def _parse_container(obj: Any) -> Any:
    if isinstance(obj, ListContainer):
        return [_parse_container(item) for item in obj]
    elif isinstance(obj, Container):
        return {key: _parse_container(obj[key]) for key in obj.keys() if key != "_io"}
    elif type(obj) == bytes and len(obj) == 32:
        return str(Pubkey.from_bytes(obj))
    elif type(obj) == str:
        return obj.replace("\x00", "")
    else:
        return obj


def parse(base64_data: bytes, construct: Struct) -> dict:
    return _parse_container(construct.parse(base64_data))
