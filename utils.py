import os
import json
import hashlib

from abc import abstractmethod
from asyncio import Event
from decimal import Decimal
from typing import Callable, Any
from string import ascii_lowercase

from exceptions import NotInitializedError


def sorted_dict(obj: dict) -> dict:
    return {key: obj[key] for key in sorted(obj)}


def add_to_dict(
    obj: dict[str, Decimal | int | float], key: str, value: Decimal | int | float
) -> None:
    if key not in obj:
        obj[key] = value
    else:
        obj[key] += value  # type: ignore


def dict_add(
    dict1: dict[str, Decimal | int | float], dict2: dict[str, Decimal | int | float]
) -> None:
    for key in dict2:
        add_to_dict(dict1, key, dict2[key])


def to_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {str(key): to_json(obj[key]) for key in obj}
    elif isinstance(obj, list):
        return [to_json(value) for value in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


class GlobalContext:
    _initializers: dict[str, Event] = {}
    _cached_values: dict[str, Any] = {}

    @staticmethod
    def with_context(function: Callable) -> Callable:
        async def wrapped_function(*args: Any, **kwargs: Any) -> Any:
            key = hashlib.sha256(
                f"{id(function)}{args}{sorted_dict(kwargs)}".encode()
            ).hexdigest()
            if key not in GlobalContext._cached_values:
                if key not in GlobalContext._initializers:
                    GlobalContext._initializers[key] = Event()
                    value = await function(*args, **kwargs)
                    GlobalContext._cached_values[key] = value
                    GlobalContext._initializers[key].set()
                else:
                    await GlobalContext._initializers[key].wait()
            return GlobalContext._cached_values[key]

        return wrapped_function


class CachedClass(type):
    __instances = {}

    @staticmethod
    def __key(class_id: int, *args, **kwargs) -> str:
        return hashlib.sha256(
            f"{class_id}{args}{sorted_dict(kwargs)}".encode()
        ).hexdigest()

    def __call__(cls, *args, **kwargs):
        key = CachedClass.__key(id(cls), *args, **kwargs)
        if key not in cls.__instances:
            cls.__instances[key] = super(CachedClass, cls).__call__(*args, **kwargs)
        return cls.__instances[key]


class InitializableClass:
    @abstractmethod
    async def _initialize(self) -> None: ...

    async def initialize(self) -> None:
        if not hasattr(self, "__initializer"):
            self.__initializer = Event()
            await self._initialize()
            self.__initializer.set()
        else:
            await self.__initializer.wait()


def initialized_property(attr: str) -> Callable:
    def decorator(_) -> Callable:
        def wrapped_function(obj: Any) -> Any:
            if attr and not hasattr(obj, attr):
                raise NotInitializedError(obj)
            return getattr(obj, attr)

        return wrapped_function

    return decorator


def get_json_dictionary(path: str) -> dict:
    files = [file for file in os.listdir(path) if ".json" in file]
    data = {}
    for file in files:
        with open(f"{path}{file}", mode="r") as f:
            data[file.replace(".json", "")] = json.load(f)
    return data


def snake_to_camel(string: str) -> str:
    _string = string
    for char in ascii_lowercase:
        _string = _string.replace(f"_{char}", char.upper())
    return _string
