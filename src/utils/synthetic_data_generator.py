import json
import random
from pathlib import Path

# ================= CONFIG =================
random.seed(42)

BASE_DIR = Path("data")
PATIENT_DIR = BASE_DIR / "patients"
TRIAL_DIR = BASE_DIR / "trials"
PAIR_DIR = BASE_DIR / "pairs"

PATIENT_DIR.mkdir(exist_ok=True)
PAIR_DIR.mkdir(exist_ok=True)

TARGET_PER_LABEL_PER_TRIAL = 80
MAX_ATTEMPTS_PER_TRIAL = 5000

# ================= CONDITION GROUPS =================
CHRONIC_CONDITIONS = [
    "type 2 diabetes", "hypertension", "cardiovascular disease",
    "cancer", "chronic kidney disease", "COPD", "asthma",
    "obesity", "hyperlipidemia", "arthritis", "osteoporosis",
    "epilepsy", "multiple sclerosis", "Parkinson's disease",
    "Alzheimer's disease", "HIV/AIDS", "liver disease",
    "thyroid disorders", "autoimmune diseases", "PCOS",
    "osteoarthritis", "heart disease"
]

MENTAL_HEALTH = [
    "depression", "anxiety", "bipolar disorder",
    "schizophrenia", "ADHD", "autism spectrum disorder"
]

SYMPTOMS_ACUTE = [
    "fatigue", "dizziness", "nausea", "vomiting",
    "diarrhea", "constipation", "chronic back pain",
    "migraine", "vitamin D deficiency"
]

INFECTIOUS = [
    "tuberculosis", "hepatitis B", "hepatitis C",
    "pneumonia", "bronchitis", "sinus infections"
]

ALL_CONDITIONS = list(set(
    CHRONIC_CONDITIONS + MENTAL_HEALTH + SYMPTOMS_ACUTE + INFECTIOUS
))

# ================= PATIENT GENERATION =================
def generate_patient_for_trial(pid, trial, target_eligible: bool):
    c = trial["criteria"]

    if target_eligible:
        age = random.randint(c["min_age"], c["max_age"])
        conditions = set(c["required_conditions"])

        extras = [
            x for x in ALL_CONDITIONS
            if x not in conditions and x not in c["excluded_conditions"]
        ]
        if extras and random.random() < 0.5:
            conditions.add(random.choice(extras))
    else:
        strategy = random.choice(["age_low", "age_high", "missing_required", "has_excluded"])

        if strategy == "age_low" and c["min_age"] > 18:
            age = random.randint(18, c["min_age"] - 1)
            conditions = set(c["required_conditions"])
        elif strategy == "age_high" and c["max_age"] < 85:
            age = random.randint(c["max_age"] + 1, 85)
            conditions = set(c["required_conditions"])
        elif strategy == "missing_required" and c["required_conditions"]:
            age = random.randint(c["min_age"], c["max_age"])
            conditions = set()
        else:
            age = random.randint(c["min_age"], c["max_age"])
            conditions = set(c["required_conditions"])
            if c["excluded_conditions"]:
                conditions.add(random.choice(c["excluded_conditions"]))

    gender = random.choice(["male", "female"])
    conditions = list(conditions)

    negated = random.sample(
        [x for x in ALL_CONDITIONS if x not in conditions],
        random.randint(0, 2)
    )

    raw_text = (
        f"Patient is a {age}-year-old {gender} with "
        f"{' and '.join(conditions) if conditions else 'no significant conditions'}."
    )

    if negated:
        raw_text += f" No history of {' or '.join(negated)}."

    return {
        "patient_id": pid,
        "raw_text": raw_text,
        "metadata": {
            "age": age,
            "gender": gender,
            "conditions": conditions,
            "negated_conditions": negated,
            "source": "balanced_per_trial_v1"
        }
    }


def is_eligible(patient, trial):
    age = patient["metadata"]["age"]
    conds = set(patient["metadata"]["conditions"])
    c = trial["criteria"]

    if not (c["min_age"] <= age <= c["max_age"]):
        return False
    if not set(c["required_conditions"]).issubset(conds):
        return False
    if set(c["excluded_conditions"]) & conds:
        return False
    return True


# ================= MAIN =================
def main():
    trials = [json.load(open(f)) for f in sorted(TRIAL_DIR.glob("*.json"))]
    print(f"Loaded {len(trials)} trials")

    patient_counter = 0
    pair_counter = 0

    for trial in trials:
        eligible = 0
        not_eligible = 0
        attempts = 0

        print(f"\nGenerating data for trial {trial['trial_id']}")

        while (
            eligible < TARGET_PER_LABEL_PER_TRIAL
            or not_eligible < TARGET_PER_LABEL_PER_TRIAL
        ) and attempts < MAX_ATTEMPTS_PER_TRIAL:

            attempts += 1
            target_eligible = eligible < TARGET_PER_LABEL_PER_TRIAL
            pid = f"P_BAL_{patient_counter:05d}"

            patient = generate_patient_for_trial(pid, trial, target_eligible)
            label = int(is_eligible(patient, trial))

            if label == 1 and eligible >= TARGET_PER_LABEL_PER_TRIAL:
                continue
            if label == 0 and not_eligible >= TARGET_PER_LABEL_PER_TRIAL:
                continue

            # Save patient
            with open(PATIENT_DIR / f"{pid}.json", "w") as f:
                json.dump(patient, f, indent=2)

            pair = {
                "pair_id": f"{pid}_{trial['trial_id']}",
                "patient_id": pid,
                "trial_id": trial["trial_id"],
                "label": label,
                "reason": "Balanced per-trial synthetic generation"
            }

            with open(PAIR_DIR / f"{pair['pair_id']}.json", "w") as f:
                json.dump(pair, f, indent=2)

            patient_counter += 1
            pair_counter += 1

            if label == 1:
                eligible += 1
            else:
                not_eligible += 1

        print(
            f"  Completed → Eligible={eligible}, "
            f"Not Eligible={not_eligible}, Attempts={attempts}"
        )

        if attempts >= MAX_ATTEMPTS_PER_TRIAL:
            print("  ⚠️ Warning: Max attempts reached for this trial")

    print("\n" + "=" * 50)
    print("✅ Balanced dataset generation complete")
    print("=" * 50)
    print(f"Patients generated: {patient_counter}")
    print(f"Pairs generated   : {pair_counter}")


if __name__ == "__main__":
    main()
