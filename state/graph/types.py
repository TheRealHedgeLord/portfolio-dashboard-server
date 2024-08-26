import json

from decimal import Decimal

from exceptions import SerializationError

ValueType = str | int | Decimal | bool | dict | list


def _int_to_bytes(number: int) -> bytes:
    hex_string = hex(number)[2::]
    padded_hex_string = "0" * (len(hex_string) % 2) + hex_string
    return bytes.fromhex(padded_hex_string)


def write(value: ValueType) -> bytes:
    if isinstance(value, str):
        return b"\x00" + value.encode()
    elif isinstance(value, bool):
        return b"\x01\x01" if value else b"\x01\x00"
    elif isinstance(value, int):
        return b"\x02" + _int_to_bytes(value)
    elif isinstance(value, Decimal):
        left, right = value.as_integer_ratio()
        left_bytes = _int_to_bytes(left)
        right_bytes = _int_to_bytes(right)
        if len(left_bytes) >= len(right_bytes):
            decimal_bytes = (
                left_bytes
                + b"\x00" * (len(left_bytes) - len(right_bytes))
                + right_bytes
            )
        else:
            decimal_bytes = (
                b"\x00" * (len(right_bytes) - len(left_bytes))
                + left_bytes
                + right_bytes
            )
        return b"\x03" + decimal_bytes
    elif isinstance(value, dict) or isinstance(value, list):
        return b"\x04" + json.dumps(value).encode()


def read(value: bytes) -> ValueType:
    type_id = value[0]
    if type_id == 0:
        return value[1::].decode()
    elif type_id == 1:
        return value[1] == 1
    elif type_id == 2:
        return int.from_bytes(value[1::])
    elif type_id == 3:
        decimal_bytes = value[1::]
        size = len(decimal_bytes) // 2
        return Decimal(int.from_bytes(decimal_bytes[0:size])) / Decimal(
            int.from_bytes(decimal_bytes[size::])
        )
    elif type_id == 4:
        return json.loads(value[1::])
    else:
        raise SerializationError(value)
