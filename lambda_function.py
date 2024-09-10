import os
import json
import asyncio

from modules import MODULES
from state import RDS


async def main(module: str, method: str, args: str) -> dict | list:
    rds = RDS(api_key=os.environ.get("STATE_KEY"))
    data = await getattr(MODULES[module](rds), method)(*args)
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
        response = {"success": False, "error": str(error)}
    return {"statusCode": status_code, "body": json.dumps(response)}
