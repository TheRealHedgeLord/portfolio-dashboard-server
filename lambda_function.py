import os
import json
import traceback
import asyncio

from modules import MODULES
from state import RDS
from cache import Cache


async def main(module: str, method: str, args: str) -> dict | list:
    rds = RDS(api_key=os.environ.get("STATE_KEY"))
    await Cache.read_from_state(rds)
    data = await getattr(MODULES[module](rds), method)(*args)
    await Cache.save()
    return {"success": True, "data": data}


def lambda_handler(event, _):
    try:
        module = event["module"]
        method = event["method"]
        args = event["args"]
        status_code = 200
        response = asyncio.run(main(module, method, args))
    except Exception as error:
        status_code = 500
        response = {
            "success": False,
            "error": str(error),
            "traceback": traceback.format_exc(),
        }
    return {"statusCode": status_code, "body": json.dumps(response)}
