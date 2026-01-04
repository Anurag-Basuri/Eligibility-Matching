import json
from pathlib import Path

def load_json_dir(path: Path):
    return [json.load(open(f)) for f in path.glob("*.json")]

def load_all_data(base_dir=Path("data")):
    patients = load_json_dir(base_dir / "patients")
    trials = load_json_dir(base_dir / "trials")
    pairs = load_json_dir(base_dir / "pairs")
    return patients, trials, pairs
