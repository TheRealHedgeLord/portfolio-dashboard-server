from utils import get_json_dictionary
from pathlib import Path


ABI = get_json_dictionary(f"{Path(__file__).parent}/abis/")

ADDRESSES = get_json_dictionary(f"{Path(__file__).parent}/addresses/")

TOPIC_APPROVAL = "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
