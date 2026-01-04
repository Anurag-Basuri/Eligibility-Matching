import json
import random
import os
from pathlib import Path

# CONFIG
BASE_DIR = Path("data")
PATIENT_DIR = BASE_DIR / "patients"
TRIAL_DIR = BASE_DIR / "trials"
PAIR_DIR = BASE_DIR / "pairs"

NUM_SYNTHETIC_PATIENTS = 50

CONDITIONS_POOL = [
    "type 2 diabetes",
    "hypertension",
    "cardiovascular disease",
    "cancer",
    "chronic kidney disease",
    "heart disease"
]

# Ensure directories exist
os.makedirs(PATIENT_DIR, exist_ok=True)
os.makedirs(TRIAL_DIR, exist_ok=True)
os.makedirs(PAIR_DIR, exist_ok=True)

# SAMPLE DATA
NAMES = [ "Ankita", "Raj", "Wei", "Fatima", "Aarav", "Sourav", "Nikhil", "Priya", "Kavita", "Rohan", "Deepak", "Sneha", "Vikram", "Meera", "Aisha", "Sanjay", "Lakshmi", "Arjun", "Divya", "Karan" ]
GENDERS = ["male", "female"]

# UTILS
def anonymize_text(text):
    text = text.replace("Ankita", "NAME")
    text = text.replace("Raj", "NAME")
    text = text.replace("Wei", "NAME")
    text = text.replace("Fatima", "NAME")
    text = text.replace("Aarav", "NAME")
    text = text.replace("Sourav", "NAME")
    text = text.replace("Nikhil", "NAME")
    text = text.replace("Priya", "NAME")
    text = text.replace("Kavita", "NAME")
    text = text.replace("Rohan", "NAME")
    text = text.replace("Deepak", "NAME")
    text = text.replace("Sneha", "NAME")
    text = text.replace("Vikram", "NAME")
    text = text.replace("Meera", "NAME")
    text = text.replace("Aisha", "NAME")
    text = text.replace("Sanjay", "NAME")
    text = text.replace("Lakshmi", "NAME")
    text = text.replace("Arjun", "NAME")
    text = text.replace("Divya", "NAME")
    text = text.replace("Karan", "NAME")
    
    return text.replace("year-old", "AGE-year-old")


def generate_patient(patient_id):
    age = random.randint(18, 85)
    gender = random.choice(GENDERS)

    num_conditions = random.randint(1, 2)
    conditions = random.sample(CONDITIONS_POOL, num_conditions)

    negated_conditions = random.sample(
        [c for c in CONDITIONS_POOL if c not in conditions],
        random.randint(0, 1)
    )

    name = random.choice(NAMES)

    raw_text = (
        f"{name}, a {age}-year-old {gender}, diagnosed with "
        f"{' and '.join(conditions)}."
    )

    if negated_conditions:
        raw_text += f" No history of {' or '.join(negated_conditions)}."

    anonymized_text = anonymize_text(raw_text)

    return {
        "patient_id": patient_id,
        "raw_text": raw_text,
        "anonymized_text": anonymized_text,
        "metadata": {
            "age": age,
            "gender": gender,
            "conditions": conditions,
            "negated_conditions": negated_conditions,
            "notes": "Synthetic patient record"
        }
    }


def is_eligible(patient, trial):
    age = patient["metadata"]["age"]
    conditions = set(patient["metadata"]["conditions"])

    criteria = trial["criteria"]

    if not (criteria["min_age"] <= age <= criteria["max_age"]):
        return False

    if not set(criteria["required_conditions"]).issubset(conditions):
        return False

    if set(criteria["excluded_conditions"]).intersection(conditions):
        return False

    return True


# LOAD TRIALS
trials = []
for file in TRIAL_DIR.glob("*.json"):
    with open(file, "r") as f:
        trials.append(json.load(f))

# GENERATE DATA
for i in range(NUM_SYNTHETIC_PATIENTS):
    pid = f"P_SYN_{i+1:03d}"
    patient = generate_patient(pid)

    patient_path = PATIENT_DIR / f"{pid}.json"
    with open(patient_path, "w") as f:
        json.dump(patient, f, indent=2)

    for trial in trials:
        label = int(is_eligible(patient, trial))

        pair = {
            "pair_id": f"{pid}_{trial['trial_id']}",
            "patient_id": pid,
            "trial_id": trial["trial_id"],
            "label": label,
            "reason": "Auto-generated using eligibility rules"
        }

        pair_path = PAIR_DIR / f"{pair['pair_id']}.json"
        with open(pair_path, "w") as f:
            json.dump(pair, f, indent=2)

print("✅ Synthetic data generation complete.")
