import asyncio
import sys

from dotenv import load_dotenv

load_dotenv()

from cli import run_command


if __name__ == "__main__":
    option = sys.argv[1]
    method = sys.argv[2]
    args = sys.argv[3::]
    asyncio.run(run_command(option, method, *args))
