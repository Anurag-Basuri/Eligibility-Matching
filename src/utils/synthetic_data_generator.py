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

NUM_PATIENTS = 160
TARGET_ELIGIBLE_RATIO = 0.5  # ~50% eligible pairs overall

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
def generate_patient(pid):
    age = random.randint(18, 85)
    gender = random.choice(["male", "female"])

    conditions = set()
    conditions.add(random.choice(CHRONIC_CONDITIONS))

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

    raw_text = (
        f"Patient is a {age}-year-old {gender} with "
        f"{' and '.join(conditions)}."
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
            "source": "balanced_160_patients_v1"
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
    trials = [json.load(open(f)) for f in sorted(TRIAL_DIR.glob("*.json"))]
    print(f"Loaded {len(trials)} trials")

    patients = []
    patient_id = 0

    # ---- STEP 1: Force eligible patients per trial ----
    ELIGIBLE_PER_TRIAL = 20

    for trial in trials:
        count = 0
        attempts = 0

        while count < ELIGIBLE_PER_TRIAL and attempts < 1000:
            attempts += 1
            pid = f"P_BAL_{patient_id:03d}"
            patient = generate_patient(pid)

            if is_eligible(patient, trial):
                patients.append(patient)
                patient_id += 1
                count += 1

        print(f"Trial {trial['trial_id']}: forced eligible = {count}")

    # ---- STEP 2: Fill remaining patients randomly ----
    while len(patients) < NUM_PATIENTS:
        pid = f"P_BAL_{patient_id:03d}"
        patients.append(generate_patient(pid))
        patient_id += 1

    # ---- STEP 3: Save patients ----
    for p in patients:
        with open(PATIENT_DIR / f"{p['patient_id']}.json", "w") as f:
            json.dump(p, f, indent=2)

    # ---- STEP 4: Generate all pairs ----
    total_eligible = 0
    total_pairs = 0

    for p in patients:
        for t in trials:
            label = int(is_eligible(p, t))
            pair = {
                "pair_id": f"{p['patient_id']}_{t['trial_id']}",
                "patient_id": p["patient_id"],
                "trial_id": t["trial_id"],
                "label": label,
                "reason": "Controlled balanced generation"
            }

            with open(PAIR_DIR / f"{pair['pair_id']}.json", "w") as f:
                json.dump(pair, f, indent=2)

            total_pairs += 1
            total_eligible += label

    print(f"\nPatients generated: {len(patients)}")
    print(f"Total pairs: {total_pairs}")
    print(f"Eligible pairs: {total_eligible}")
    print(f"Eligible ratio: {total_eligible / total_pairs:.2%}")


if __name__ == "__main__":
    main()
