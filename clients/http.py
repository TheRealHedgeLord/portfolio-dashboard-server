import httpx
import json
import asyncio
import uuid

from typing import Dict, Any, Literal
from urllib.parse import urlencode
from asyncio import Queue

from exceptions import HTTPException


class HTTPClient:
    _name: str  # override
    _base_url: str  # override
    _request_limit: float  # override

    def __init__(self) -> None:
        self.__queue = Queue()
        self.__unblock()

    async def _call(
        self,
        method: Literal["get", "post"],
        endpoint: str = "",
        parameters: Dict[str, Any] = {},
        data: str = "",
        headers: Dict[str, str] = {},
        timeout: int = 15,
    ) -> Any:
        await self.__queue.get()
        asyncio.create_task(self.__start_counter())
        return await self.__call(method, endpoint, parameters, data, headers, timeout)

    def __unblock(self) -> None:
        if self.__queue.empty():
            self.__queue.put_nowait(uuid.uuid4().hex)

    async def __start_counter(self) -> None:
        await asyncio.sleep(self._request_limit)
        self.__unblock()

    async def __call(
        self,
        method: Literal["get", "post"],
        endpoint: str,
        parameters: Dict[str, Any],
        data: str,
        headers: Dict[str, str],
        timeout: int,
    ) -> Any:
        url = (
            self._base_url
            + endpoint
            + (f"?{urlencode(parameters)}" if parameters else "")
        )
        async with httpx.AsyncClient(timeout=timeout) as client:
            kwargs = {}
            if data:
                kwargs["data"] = data
            if headers:
                kwargs["headers"] = headers
            response = await getattr(client, method)(url, **kwargs)
            if response.status_code != 200:
                text = response.text
                if "<!DOCTYPE html>" in text:
                    raise HTTPException(
                        self._name, response.status_code, "blocked by server"
                    )
                else:
                    raise HTTPException(self._name, response.status_code, response.text)
            data = json.loads(response.text)
        return data
