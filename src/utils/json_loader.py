import json
from pathlib import Path


def load_json_dir(path: Path):
    data = []
    for f in path.glob("*.json"):
        try:
            if f.stat().st_size == 0:
                # Skip empty files
                continue
            with open(f, "r", encoding="utf-8") as file:
                data.append(json.load(file))
        except json.JSONDecodeError:
            print(f"⚠️ Skipping invalid JSON file: {f.name}")
        except Exception as e:
            print(f"⚠️ Error loading {f.name}: {e}")
    return data


def load_all_data(base_dir=Path("data")):
    patients = load_json_dir(base_dir / "patients")
    trials = load_json_dir(base_dir / "trials")
    pairs = load_json_dir(base_dir / "pairs")
    return patients, trials, pairs
