import sys

from dotenv import load_dotenv

load_dotenv()

from lambda_function import lambda_handler

if __name__ == "__main__":
    argv = sys.argv
    event = {"module": argv[1], "method": argv[2], "args": list(argv[3::])}
    response = lambda_handler(event, None)
    if response["statusCode"] != 200:
        raise Exception(str(response))
