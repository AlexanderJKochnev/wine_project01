import json
from pathlib import Path
from app.core.utils.alchemy_utils import model_to_dict
from app.core.utils.common_utils import flatten_dict, jprint

def read_json(filename: str) -> dict:
    source = Path(__file__).resolve().parent.joinpath(filename)
    if source.exists():
        with open(source) as f:
            data = json.load(f)
            return data
    return None


jprint(read_json('relation_output.json'))