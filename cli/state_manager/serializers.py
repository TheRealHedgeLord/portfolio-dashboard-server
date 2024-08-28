import json

from typing import Any
from base64 import b64decode
from decimal import Decimal

from exceptions import InvalidValue


def _decode_obj(obj: Any) -> Any:
    if isinstance(obj, list):
        return [_decode_obj(value) for value in obj]
    elif isinstance(obj, dict):
        return {key: _decode_obj(obj[key]) for key in obj}
    elif isinstance(obj, str):
        type_id = obj[0]
        value = obj[1::]
        if type_id == "0":
            return value
        elif type_id == "1":
            return b64decode(value)
        elif type_id == "2":
            return Decimal(value)
        else:
            raise InvalidValue("encoded string", obj)
    else:
        return obj


def from_cli_arg(cli_arg: str) -> dict | list:
    return _decode_obj(json.loads(b64decode(cli_arg)))
