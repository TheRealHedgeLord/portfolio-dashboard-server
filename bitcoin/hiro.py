from clients.http import HTTPClient


class HiroClient(HTTPClient):
    _name = "Hiro"
    _base_url = "https://api.hiro.so"
    _request_limit = 1

    async def get_ordinals(self, wallet: str):
        response = await self._call(
            "get",
            endpoint="/ordinals/v1/inscriptions",
            parameters={"address": wallet},
            headers={"Accept": "application/json"},
        )
        return [inscription["number"] for inscription in response["results"]]
