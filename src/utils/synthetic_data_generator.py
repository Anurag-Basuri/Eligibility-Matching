import json
import random
import os
import re
import argparse
from datetime import datetime
from pathlib import Path

# CONFIG
BASE_DIR = Path("data")
PATIENT_DIR = BASE_DIR / "patients"
TRIAL_DIR = BASE_DIR / "trials"
PAIR_DIR = BASE_DIR / "pairs"

NUM_SYNTHETIC_PATIENTS = 50

# Expanded condition pool to match existing patient and trial data
CONDITIONS_POOL = [
    "type 2 diabetes",
    "hypertension",
    "cardiovascular disease",
    "cancer",
    "chronic kidney disease",
    "heart disease",
    "PCOS",
    "osteoarthritis",
    "COPD",
    "vitamin D deficiency",
    "migraine",
    "hypothyroidism",
    "iron deficiency anemia",
    "stroke",
    "myocardial infarction",
    "pregnancy",
    "depression",
    "anxiety",
    "asthma",
    "obesity",
    "hyperlipidemia",
    "allergies",
    "arthritis",
    "eczema",
    "psoriasis",
    "tuberculosis",
    "HIV/AIDS",
    "hepatitis B",
    "hepatitis C",
    "Alzheimer's disease",
    "Parkinson's disease",
    "multiple sclerosis",
    "epilepsy",
    "glaucoma",
    "cataracts",
    "chronic liver disease",
    "gout",
    "rheumatoid arthritis",
    "Crohn's disease",
    "ulcerative colitis",
    "celiac disease",
    "anemia",
    "leukemia",
    "lymphoma",
    "sickle cell disease",
    "hemophilia",
    "Cushing's syndrome",
    "Addison's disease",
    "polycystic kidney disease",
    "endometriosis",
    "menopause",
    "infertility"
]

# Ensure directories exist
os.makedirs(PATIENT_DIR, exist_ok=True)
os.makedirs(TRIAL_DIR, exist_ok=True)
os.makedirs(PAIR_DIR, exist_ok=True)

# SAMPLE DATA
MALE_NAMES = [
    "Raj Kumar", "Aarav Sharma", "Sourav Patel", "Nikhil Singh", "Rohan Mehta",
    "Deepak Gupta", "Vikram Rao", "Sanjay Verma", "Arjun Joshi", "Karan Dhillon"
]

FEMALE_NAMES = [
    "Ankita Sharma", "Wei Ling", "Fatima Khan", "Priya Nair", "Kavita Rao",
    "Sneha Iyer", "Meera Menon", "Aisha Siddiqui", "Lakshmi Reddy", "Divya Kapoor"
]

# UTILS
def anonymize_text(text):
    # Replace any full name or given name from our lists with a single placeholder
    all_names = MALE_NAMES + FEMALE_NAMES
    for name in all_names:
        # replace full name occurrences (case-insensitive)
        pattern = re.compile(r"\b" + re.escape(name) + r"\b", flags=re.IGNORECASE)
        text = pattern.sub("PATIENT_NAME", text)
        # also replace given name only (first token) to catch partial mentions
        first_name = name.split()[0]
        pattern2 = re.compile(r"\b" + re.escape(first_name) + r"\b", flags=re.IGNORECASE)
        text = pattern2.sub("PATIENT_NAME", text)

    return text.replace("year-old", "AGE-year-old")


def generate_patient(patient_id):
    age = random.randint(15, 85)

    # pick a name from gendered lists; gender comes from the name chosen
    if random.random() <= 0.5:
        name = random.choice(MALE_NAMES)
        gender = "male"
    else:
        name = random.choice(FEMALE_NAMES)
        gender = "female"

    num_conditions = random.randint(1, 2)
    conditions = random.sample(CONDITIONS_POOL, num_conditions)

    negated_candidates = [c for c in CONDITIONS_POOL if c not in conditions]
    negated_conditions = random.sample(negated_candidates, k=random.randint(0, min(1, len(negated_candidates))))

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
def parse_args():
    parser = argparse.ArgumentParser(description="Generate synthetic patients and pair files (batchable).")
    parser.add_argument("--num", type=int, default=NUM_SYNTHETIC_PATIENTS, help="Number of synthetic patients to generate")
    parser.add_argument("--batch", type=str, default=None, help="Batch name/tag to include in generated IDs (default: timestamp)")
    parser.add_argument("--skip-pairs", action="store_true", help="Generate patients only, skip pair files")
    return parser.parse_args()


def main():
    args = parse_args()
    num = args.num
    batch = args.batch or datetime.now().strftime("%Y%m%d%H%M%S")

    # Generate patients and pairs for this batch
    for i in range(num):
        pid = f"P_SYN_{batch}_{i+1:03d}"
        patient = generate_patient(pid)

        patient_path = PATIENT_DIR / f"{pid}.json"
        with open(patient_path, "w") as f:
            json.dump(patient, f, indent=2)

        if args.skip_pairs:
            continue

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

    print(f"✅ Synthetic data generation complete. batch={batch} patients={num}")


if __name__ == "__main__":
    main()
