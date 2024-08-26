import json

from pathlib import Path

with open(f"{Path(__file__).parent}/ordinals.json", mode="r") as file:
    ORDINALS = json.load(file)
