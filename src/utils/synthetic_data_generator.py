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

TARGET_PER_LABEL = 80
MAX_ATTEMPTS = 5000

# ================= CONDITION GROUPS =================
CHRONIC_CONDITIONS = [
    "type 2 diabetes", "hypertension", "cardiovascular disease",
    "cancer", "chronic kidney disease", "COPD", "asthma",
    "obesity", "hyperlipidemia", "arthritis", "osteoporosis",
    "epilepsy", "multiple sclerosis", "Parkinson's disease",
    "Alzheimer's disease", "HIV/AIDS", "liver disease",
    "thyroid disorders", "autoimmune diseases"
]

MENTAL_HEALTH = [
    "depression", "anxiety", "bipolar disorder",
    "schizophrenia", "ADHD", "autism spectrum disorder"
]

SYMPTOMS_ACUTE = [
    "fatigue", "dizziness", "nausea", "vomiting",
    "diarrhea", "constipation", "chronic back pain"
]

INFECTIOUS = [
    "tuberculosis", "hepatitis B", "hepatitis C",
    "pneumonia", "bronchitis", "sinus infections"
]

ALL_CONDITIONS = (
    CHRONIC_CONDITIONS +
    MENTAL_HEALTH +
    SYMPTOMS_ACUTE +
    INFECTIOUS
)

# ================= PATIENT GENERATION =================
def generate_patient(pid):
    age = random.randint(18, 85)
    gender = random.choice(["male", "female"])

    conditions = set()

    # Always at least one chronic condition
    conditions.add(random.choice(CHRONIC_CONDITIONS))

    # Optional secondary conditions
    if random.random() < 0.6:
        conditions.add(random.choice(MENTAL_HEALTH))
    if random.random() < 0.4:
        conditions.add(random.choice(SYMPTOMS_ACUTE))
    if random.random() < 0.3:
        conditions.add(random.choice(INFECTIOUS))

    conditions = list(conditions)

    negated = random.sample(
        [c for c in ALL_CONDITIONS if c not in conditions],
        random.randint(0, 2)
    )

    templates = [
        "Patient is a {age}-year-old {gender} with {conds}.",
        "A {age}-year-old {gender} diagnosed with {conds}.",
        "{age}-year-old {gender} patient with a history of {conds}."
    ]

    raw_text = random.choice(templates).format(
        age=age,
        gender=gender,
        conds=" and ".join(conditions)
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
            "source": "balanced_synthetic_v2"
        }
    }

# ================= ELIGIBILITY =================
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
    trials = [json.load(open(f)) for f in TRIAL_DIR.glob("*.json")]

    patient_id_counter = 0
    pair_count = 0

    for trial in trials:
        eligible = 0
        not_eligible = 0
        attempts = 0

        while (eligible < TARGET_PER_LABEL or not_eligible < TARGET_PER_LABEL) and attempts < MAX_ATTEMPTS:
            attempts += 1
            pid = f"P_BAL_{patient_id_counter:05d}"
            patient = generate_patient(pid)

            label = int(is_eligible(patient, trial))

            if label == 1 and eligible >= TARGET_PER_LABEL:
                continue
            if label == 0 and not_eligible >= TARGET_PER_LABEL:
                continue

            # Save patient
            with open(PATIENT_DIR / f"{pid}.json", "w") as f:
                json.dump(patient, f, indent=2)

            pair = {
                "pair_id": f"{pid}_{trial['trial_id']}",
                "patient_id": pid,
                "trial_id": trial["trial_id"],
                "label": label,
                "reason": "Balanced synthetic generation with controlled diversity"
            }

            with open(PAIR_DIR / f"{pair['pair_id']}.json", "w") as f:
                json.dump(pair, f, indent=2)

            patient_id_counter += 1
            pair_count += 1

            if label == 1:
                eligible += 1
            else:
                not_eligible += 1

        print(
            f"Trial {trial['trial_id']} → "
            f"Eligible: {eligible}, Not Eligible: {not_eligible}, Attempts: {attempts}"
        )

    print("\n✅ Balanced dataset generation complete")
    print(f"Patients generated: {patient_id_counter}")
    print(f"Pairs generated   : {pair_count}")

if __name__ == "__main__":
    main()
