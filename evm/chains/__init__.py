import json

from os import environ
from functools import cache
from pathlib import Path


@cache
def get_chain_meta(name: str) -> tuple[int, str, str]:
    with open(f"{Path(__file__).parent}/{name}.json", mode="r") as file:
        meta = json.load(file)
        rpc_url = (
            environ[meta["rpc_url"][1::]]
            if meta["rpc_url"][0] == "$"
            else meta["rpc_url"]
        )
        return meta["network_id"], rpc_url, meta["symbol"]
