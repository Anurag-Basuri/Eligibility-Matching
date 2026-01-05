import json
import random
from pathlib import Path

# ================= PATHS AND CONSTANTS =================
BASE_DIR = Path("data")
PATIENT_DIR = BASE_DIR / "patients"
TRIAL_DIR = BASE_DIR / "trials"
PAIR_DIR = BASE_DIR / "pairs"

DEFAULT_NUM_PATIENTS = 160

TARGET_PER_LABEL = DEFAULT_NUM_PATIENTS // 2

# ================= DISEASE CONDITIONS =================
CONDITIONS = [
    "type 2 diabetes",
    "hypertension",
    "cardiovascular disease",
    "cancer",
    "chronic kidney disease",
    "heart disease",
    "PCOS",
    "COPD",
    "vitamin D deficiency",
    "migraine",
    "hypothyroidism",
    "depression",
    "anxiety",
    "asthma",
    "obesity",
    "hyperlipidemia",
    "smoking",
    "arthritis",
    "osteoporosis",
    "allergies",
    "eczema",
    "GERD",
    "sleep apnea",
    "IBS",
    "anemia",
    "fibromyalgia",
    "chronic back pain",
    "glaucoma",
    "hearing loss",
    "cataracts",
    "psoriasis",
    "epilepsy",
    "multiple sclerosis",
    "Parkinson's disease",
    "Alzheimer's disease",
    "HIV/AIDS",
    "liver disease",
    "thyroid disorders",
    "autoimmune diseases",
    "dehydration",
    "dizziness",
    "fatigue",
    "constipation",
    "diarrhea",
    "nausea",
    "vomiting",
    "skin infections",
    "urinary tract infections",
    "sinus infections",
    "bronchitis",
    "pneumonia",
    "tuberculosis",
    "hepatitis B",
    "hepatitis C",
    "menopause",
    "endometriosis",
    "infertility",
    "gestational diabetes",
    "pre-eclampsia",
    "postpartum depression",
    "ADHD",
    "autism spectrum disorder",
    "bipolar disorder",
    "schizophrenia",
]

# ================= PATIENT GENERATION =================
def generate_patient(pid):
    age = random.randint(18, 85)
    gender = random.choice(["male", "female"])

    num_conditions = random.randint(1, 3)
    conditions = random.sample(CONDITIONS, num_conditions)

    negated = random.sample(
        [c for c in CONDITIONS if c not in conditions],
        random.randint(0, 2)
    )

    raw_text = (
        f"Patient, a {age}-year-old {gender}, diagnosed with "
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
            "source": "balanced_synthetic"
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

    patient_count = 0
    pair_count = 0

    for trial in trials:
        eligible = 0
        not_eligible = 0

        while eligible < TARGET_PER_LABEL or not_eligible < TARGET_PER_LABEL:
            pid = f"P_BAL_{patient_count:04d}"
            patient = generate_patient(pid)

            label = int(is_eligible(patient, trial))

            if label == 1 and eligible >= TARGET_PER_LABEL:
                continue
            if label == 0 and not_eligible >= TARGET_PER_LABEL:
                continue

            # save patient
            with open(PATIENT_DIR / f"{pid}.json", "w") as f:
                json.dump(patient, f, indent=2)

            pair = {
                "pair_id": f"{pid}_{trial['trial_id']}",
                "patient_id": pid,
                "trial_id": trial["trial_id"],
                "label": label,
                "reason": "Balanced synthetic generation"
            }

            with open(PAIR_DIR / f"{pair['pair_id']}.json", "w") as f:
                json.dump(pair, f, indent=2)

            patient_count += 1
            pair_count += 1

            if label == 1:
                eligible += 1
            else:
                not_eligible += 1

        print(
            f"Trial {trial['trial_id']} → "
            f"Eligible: {eligible}, Not Eligible: {not_eligible}"
        )

    print("\n✅ Balanced dataset generation complete")
    print(f"Patients generated: {patient_count}")
    print(f"Pairs generated   : {pair_count}")

if __name__ == "__main__":
    main()