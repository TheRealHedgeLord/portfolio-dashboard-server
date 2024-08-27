import json

from typing import Literal
from decimal import Decimal
from base64 import b64encode, b64decode

from exceptions import SerializationError

ColumnType = Literal["string", "integer", "decimal", "bool", "json", "bytes"]
SQLiteType = Literal["TEXT", "INTEGER", "BLOB"]
ValueType = str | int | Decimal | bool | dict | list | bytes
SQLiteValueType = str | int | bytes

COLUMN_TYPE_MAP: dict[ColumnType, SQLiteType] = {
    "string": "TEXT",
    "integer": "INTEGER",
    "decimal": "BLOB",
    "bool": "BLOB",
    "json": "BLOB",
    "bytes": "BLOB",
}


def _bytes_to_decimal(value: bytes) -> Decimal:
    body = value[1::]
    size = len(body) // 2
    return Decimal(int.from_bytes(body[0:size])) / Decimal(int.from_bytes(body[size::]))


def _bytes_to_bool(value: bytes) -> bool:
    return value[1] != 0


def _bytes_to_json(value: bytes) -> dict | list:
    return json.loads(value[1::])


def _decimal_to_sqlite(value: Decimal) -> str:
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
    return f"x'01{decimal_hex}'"


def _bool_to_sqlite(value: bool) -> str:
    return "x'0001'" if value else "x'0000'"


def _json_to_sqlite(value: dict | list) -> str:
    json_hex_string = json.dumps(value).encode().hex()
    return f"x'02{json_hex_string}'"


def _bytes_to_sqlite(value: bytes) -> str:
    return f"x'03{value.hex()}'"


def from_sqlite(value: SQLiteValueType) -> ValueType | None:
    if isinstance(value, int) or isinstance(value, str):
        return value
    elif isinstance(value, bytes):
        type_id = value[0]
        if type_id == 0:
            return _bytes_to_bool(value)
        elif type_id == 1:
            return _bytes_to_decimal(value)
        elif type_id == 2:
            return _bytes_to_json(value)
        elif type_id == 3:
            return value[1::]
        else:
            raise SerializationError(value)
    elif isinstance(value, bytearray) or isinstance(value, memoryview):
        return from_sqlite(bytes(value))


def to_sqlite(value: ValueType) -> str:
    if isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, bool):
        return _bool_to_sqlite(value)
    elif isinstance(value, int):
        return str(value)
    elif isinstance(value, Decimal):
        return _decimal_to_sqlite(value)
    elif isinstance(value, dict) or isinstance(value, list):
        return _json_to_sqlite(value)
    else:
        return _bytes_to_sqlite(value)


def to_parsed(sqlite_value: SQLiteValueType) -> str:
    if isinstance(sqlite_value, str):
        return "0" + sqlite_value
    elif isinstance(sqlite_value, int):
        return "1" + str(sqlite_value)
    else:
        return "2" + b64encode(sqlite_value).decode()


def from_parsed(parsed_value: str) -> SQLiteValueType:
    type_id = parsed_value[0]
    value = parsed_value[1::]
    if type_id == "0":
        return value
    elif type_id == "1":
        return int(value)
    elif type_id == "2":
        return b64decode(value)
    else:
        raise ValueError(f"invalid parsed value {parsed_value}")
