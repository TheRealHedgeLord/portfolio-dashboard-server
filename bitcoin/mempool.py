from clients.http import HTTPClient
from decimal import Decimal


class MempoolClient(HTTPClient):
    _name = "Mempool"
    _base_url = "https://mempool.space"
    _request_limit = 0.1

    async def get_wallet_balance(self, address: str) -> Decimal:
        response = await self._call("get", endpoint=f"/api/address/{address}/utxo")
        sats = sum([utxo["value"] for utxo in response])
        return Decimal(sats) / Decimal(1e8)
