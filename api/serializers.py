import json

from typing import Any
from base64 import b64encode
from decimal import Decimal


def encode_obj(obj: Any) -> Any:
    if isinstance(obj, list):
        return [encode_obj(value) for value in obj]
    elif isinstance(obj, dict):
        return {key: encode_obj(obj[key]) for key in obj}
    elif isinstance(obj, str):
        return "0" + obj
    elif isinstance(obj, bytes):
        return "1" + b64encode(obj).decode()
    elif isinstance(obj, Decimal):
        return "2" + str(obj)
    else:
        return obj


def to_cli_arg(args: list | dict) -> str:
    return b64encode(json.dumps(encode_obj(args)).encode()).decode()
