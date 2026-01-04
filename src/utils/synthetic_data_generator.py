import json
import random
import os
import re
import argparse
from collections import Counter
from pathlib import Path

# =========================
# CONFIG
# =========================
BASE_DIR = Path("data")
PATIENT_DIR = BASE_DIR / "patients"
TRIAL_DIR = BASE_DIR / "trials"
PAIR_DIR = BASE_DIR / "pairs"

DEFAULT_NUM_PATIENTS = 160

# =========================
# CONDITION POOL
# =========================
CONDITIONS_POOL = [
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

CONDITION_WEIGHTS = {
    "type 2 diabetes": 6,
    "hypertension": 8,
    "cardiovascular disease": 4,
    "cancer": 2,
    "chronic kidney disease": 2,
    "heart disease": 4,
    "PCOS": 2,
    "COPD": 3,
    "vitamin D deficiency": 3,
    "migraine": 3,
    "hypothyroidism": 3,
    "depression": 4,
    "anxiety": 4,
    "asthma": 3,
    "obesity": 6,
    "hyperlipidemia": 5,
    "smoking": 4,
    "arthritis": 4,
    "osteoporosis": 2,
    "allergies": 3,
    "eczema": 2,
    "GERD": 2,
    "sleep apnea": 2,
    "IBS": 2,
    "anemia": 2,
    "fibromyalgia": 1,
    "chronic back pain": 2,
    "glaucoma": 1,
    "hearing loss": 1,
    "cataracts": 1,
    "psoriasis": 2,
    "epilepsy": 1,
    "multiple sclerosis": 1,
    "Parkinson's disease": 1,
    "Alzheimer's disease": 1,
    "HIV/AIDS": 1,
    "liver disease": 1,
    "thyroid disorders": 2,
    "autoimmune diseases": 1,
    "dehydration": 1,
    "dizziness": 1,
    "fatigue": 1,
    "constipation": 1,
    "diarrhea": 1,
    "nausea": 1,
    "vomiting": 1,
    "skin infections": 1,
    "urinary tract infections": 1,
    "sinus infections": 1,
    "bronchitis": 1,
    "pneumonia": 1,
    "tuberculosis": 1,
    "hepatitis B": 1,
    "hepatitis C": 1,
    "menopause": 1,
    "endometriosis": 1,
    "infertility": 1,
    "gestational diabetes": 1,
    "pre-eclampsia": 1,
    "postpartum depression": 1,
    "ADHD": 2,
    "autism spectrum disorder": 1,
    "bipolar disorder": 1,
    "schizophrenia": 1,
}

WEIGHTS = [CONDITION_WEIGHTS.get(c, 1) for c in CONDITIONS_POOL]

# =========================
# UTILITIES
# =========================
def choose_age():
    buckets = [
        (18, 30, 0.2),
        (31, 45, 0.3),
        (46, 65, 0.35),
        (66, 85, 0.15),
    ]
    r = random.random()
    acc = 0
    for lo, hi, p in buckets:
        acc += p
        if r <= acc:
            return random.randint(lo, hi)
    return random.randint(18, 85)


def choose_conditions():
    k = random.choices([0, 1, 2, 3], weights=[5, 55, 25, 15])[0]
    if k == 0:
        return []

    pool = CONDITIONS_POOL.copy()
    weights = WEIGHTS.copy()
    chosen = []

    for _ in range(k):
        if not pool:
            break
        c = random.choices(pool, weights=weights)[0]
        idx = pool.index(c)
        chosen.append(c)
        pool.pop(idx)
        weights.pop(idx)

    # correlations
    if (
        "type 2 diabetes" in chosen
        and "obesity" not in chosen
        and random.random() < 0.4
    ):
        chosen.append("obesity")
    if (
        "hypertension" in chosen
        and "hyperlipidemia" not in chosen
        and random.random() < 0.3
    ):
        chosen.append("hyperlipidemia")

    return list(dict.fromkeys(chosen))


def generate_raw_text(age, gender, conditions):
    templates = [
        "{name}, a {age}-year-old {gender}, diagnosed with {conds}.",
        "{name} is a {age}-year-old {gender} with {conds}.",
        "{name}, aged {age}, has a history of {conds}.",
    ]
    name = "Patient"
    conds = " and ".join(conditions) if conditions else "no chronic medical conditions"
    return random.choice(templates).format(
        name=name, age=age, gender=gender, conds=conds
    )


def generate_patient(pid):
    age = choose_age()
    gender = random.choice(["male", "female"])
    conditions = choose_conditions()

    negated = random.sample(
        [c for c in CONDITIONS_POOL if c not in conditions], random.randint(0, 2)
    )

    raw_text = generate_raw_text(age, gender, conditions)
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
            "source": "synthetic_v3",
        },
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


# =========================
# MAIN
# =========================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num", type=int, default=DEFAULT_NUM_PATIENTS)
    args = parser.parse_args()

    PATIENT_DIR.mkdir(exist_ok=True)
    PAIR_DIR.mkdir(exist_ok=True)

    trials = [json.load(open(f)) for f in TRIAL_DIR.glob("*.json")]

    start_idx = len(list(PATIENT_DIR.glob("P_SYN_*.json")))
    total_pairs = 0
    eligible_pairs = 0

    for i in range(args.num):
        pid = f"P_SYN_{start_idx + i + 1:03d}"
        patient = generate_patient(pid)

        with open(PATIENT_DIR / f"{pid}.json", "w") as f:
            json.dump(patient, f, indent=2)

        for t in trials:
            label = int(is_eligible(patient, t))
            eligible_pairs += label
            total_pairs += 1

            pair = {
                "pair_id": f"{pid}_{t['trial_id']}",
                "patient_id": pid,
                "trial_id": t["trial_id"],
                "label": label,
                "reason": "Auto-generated using rule-based eligibility logic",
            }

            with open(PAIR_DIR / f"{pair['pair_id']}.json", "w") as f:
                json.dump(pair, f, indent=2)

    print(f"✅ Generated {args.num} patients")
    print(f"Eligibility rate: {eligible_pairs / max(1, total_pairs):.2f}")


if __name__ == "__main__":
    main()
