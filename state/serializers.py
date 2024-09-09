import json

from decimal import Decimal
from base64 import b64decode
from enum import StrEnum, IntEnum

from exceptions import SerializationError


StateDataType = bool | int | str | Decimal | list | dict | bytes


class ColumnType(StrEnum):
    bool = "CHAR(1)"
    integer = "BIGINT"
    string = "BLOB"
    decimal = "BLOB"
    json = "BLOB"
    bytes = "BLOB"


class BlobTypeCode(IntEnum):
    string = 0
    decimal = 1
    json = 2
    bytes = 3


def serialize_bool(value: bool) -> str:
    return "'1'" if value else "'0'"


def serialize_integer(value: int) -> str:
    return str(value)


def serialize_string(value: str) -> str:
    return f"x'{(BlobTypeCode.string.to_bytes() + value.encode()).hex()}'"


def serialize_decimal(value: Decimal) -> str:
    left, right = value.as_integer_ratio()
    left_hex = hex(left)[2::]
    left_hex_padded = "0" * (len(left_hex) % 2) + left_hex
    left_length = len(left_hex_padded)
    right_hex = hex(right)[2::]
    right_hex_padded = "0" * (len(right_hex) % 2) + right_hex
    right_length = len(right_hex_padded)
    if len(left_hex_padded) >= len(right_hex_padded):
        decimal_hex = (
            left_hex_padded + "0" * (left_length - right_length) + right_hex_padded
        )
    else:
        decimal_hex = (
            "0" * (right_length - left_length) + left_hex_padded + right_hex_padded
        )
    return f"x'{BlobTypeCode.decimal.to_bytes().hex()}{decimal_hex}'"


def serialize_json(value: list | dict) -> str:
    return f"x'{(BlobTypeCode.json.to_bytes() + json.dumps(value).encode()).hex()}'"


def serialize_bytes(value: bytes) -> str:
    return f"x'{(BlobTypeCode.bytes.to_bytes() + value).hex()}'"


def serialize(value: StateDataType) -> str:
    if isinstance(value, bool):
        return serialize_bool(value)
    elif isinstance(value, int):
        return serialize_integer(value)
    elif isinstance(value, str):
        return serialize_string(value)
    elif isinstance(value, Decimal):
        return serialize_decimal(value)
    elif isinstance(value, list) or isinstance(value, dict):
        return serialize_json(value)
    else:
        return serialize_bytes(value)


def deserialize_string(value: bytes) -> str:
    return value.decode()


def deserialize_decimal(value: bytes) -> Decimal:
    size = len(value) // 2
    return Decimal(int.from_bytes(value[0:size])) / Decimal(
        int.from_bytes(value[size::])
    )


def deserialize_json(value: bytes) -> list | dict:
    return json.loads(value)


def deserialize(value: int | str) -> StateDataType:
    if value == "1":
        return True
    elif value == "0":
        return False
    elif isinstance(value, int):
        return value
    else:
        blob_data = b64decode(value)
        type_code = blob_data[0]
        content = blob_data[1::]
        if type_code == BlobTypeCode.string:
            return deserialize_string(content)
        elif type_code == BlobTypeCode.decimal:
            return deserialize_decimal(content)
        elif type_code == BlobTypeCode.json:
            return deserialize_json(content)
        elif type_code == BlobTypeCode.bytes:
            return content
        else:
            raise SerializationError(value)
