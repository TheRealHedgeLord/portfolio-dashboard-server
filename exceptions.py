from typing_extensions import Self
from typing import Any


class NotInitializedError(BaseException):
    def __init__(self, obj: Any) -> None:
        super().__init__(Exception(f"{obj} not initialized"))


class NotExistError(BaseException):
    def __init__(self, class_id: Any, instance_id: Any) -> None:
        super().__init__(Exception(f"{class_id} {instance_id} does not exist"))


class InvalidURL(BaseException):
    def __init__(self) -> None:
        super().__init__(Exception("invalid url"))


class SerializationError(BaseException):
    def __init__(self, value: Any) -> None:
        super().__init__(Exception(f"cannot (de)serialize value {value}"))


class HTTPException(BaseException):
    def __init__(self, name: str, status_code: int, message: str) -> None:
        super().__init__(Exception(f"({name}) status code {status_code}, {message}"))
