import json
from pathlib import Path

# Directories
BASE = Path("data")
PATIENT_DIR = BASE / "patients"
TRIAL_DIR = BASE / "trials"
PAIR_DIR = BASE / "pairs"

PAIR_DIR.mkdir(parents=True, exist_ok=True)


def check_eligibility(patient, trial):
    """
    Returns (label, reason) where label is 1 (eligible) or 0 (not eligible),
    and reason is a human-readable explanation.
    """
    age = patient["metadata"].get("age")
    conditions = set(patient["metadata"].get("conditions", []))
    criteria = trial["criteria"]

    reasons_fail = []

    # Age check
    if age is None:
        reasons_fail.append("Patient age missing")
    else:
        if age < criteria["min_age"]:
            reasons_fail.append(f"Patient age ({age}) is below the minimum required age ({criteria['min_age']})")
        elif age > criteria["max_age"]:
            reasons_fail.append(f"Patient age ({age}) exceeds the maximum allowed age ({criteria['max_age']})")

    # Required conditions check
    required = set(criteria.get("required_conditions", []))
    missing = required - conditions
    if missing:
        reasons_fail.append(f"Missing required condition(s): {', '.join(sorted(missing))}")

    # Excluded conditions check
    excluded = set(criteria.get("excluded_conditions", []))
    present_excluded = excluded & conditions
    if present_excluded:
        reasons_fail.append(f"Has excluded condition(s): {', '.join(sorted(present_excluded))}")

    if reasons_fail:
        return 0, "; ".join(reasons_fail) + "."
    else:
        age_ok = f"Age {age} is within range [{criteria['min_age']}-{criteria['max_age']}]" if age is not None else "Age OK"
        conds_ok = f"has required condition(s): {', '.join(sorted(required))}" if required else "no specific conditions required"
        excluded_ok = f"none of the excluded conditions ({', '.join(sorted(excluded))}) are present" if excluded else "no exclusions apply"
        return 1, f"{age_ok}; {conds_ok}; {excluded_ok}."


def load_json_files(directory: Path):
    items = []
    for p in sorted(directory.glob("*.json")):
        try:
            with open(p, "r", encoding="utf-8") as fh:
                items.append(json.load(fh))
        except Exception as e:
            print(f"Skipping {p}: failed to load JSON: {e}")
    return items


def main():
    patients = load_json_files(PATIENT_DIR)
    trials = load_json_files(TRIAL_DIR)

    if not patients:
        print("No patient files found in", PATIENT_DIR)
        return
    if not trials:
        print("No trial files found in", TRIAL_DIR)
        return

    total = 0
    eligible = 0

    for patient in patients:
        pid = patient.get("patient_id")
        if not pid:
            print("Skipping patient without patient_id")
            continue
        for trial in trials:
            tid = trial.get("trial_id")
            if not tid:
                print("Skipping trial without trial_id")
                continue

            label, reason = check_eligibility(patient, trial)
            pair = {
                "pair_id": f"{pid}_{tid}",
                "patient_id": pid,
                "trial_id": tid,
                "label": label,
                "reason": reason,
            }

            out_path = PAIR_DIR / f"{pair['pair_id']}.json"
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(pair, fh, indent=2)

            total += 1
            eligible += label

    summary = {
        "pairs_created": total,
        "eligible_pairs": eligible,
        "eligible_rate": eligible / total if total else 0.0,
    }
    summary_path = PAIR_DIR / "regenerate_summary.json"
    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(f"Wrote {total} pair files to {PAIR_DIR} ({eligible} eligible).")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
