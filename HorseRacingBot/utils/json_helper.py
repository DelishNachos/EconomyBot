from pathlib import Path
import json

def load_json(path):
    if path.exists():
        return json.load(open(path))
    return {}

def save_json(path, data):
    json.dump(data, open(path, "w"), indent=2)