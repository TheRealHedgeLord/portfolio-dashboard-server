from utils import get_json_dictionary
from pathlib import Path

FORKS = get_json_dictionary(f"{Path(__file__).parent}/")
