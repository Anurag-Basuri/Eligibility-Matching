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

# Target: total pairs per label (globally balanced)
TARGET_ELIGIBLE = 800
TARGET_NOT_ELIGIBLE = 800
MAX_PATIENTS = 5000  # safety cap

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

# ================= HELPERS =================
def get_eligibility_reason(patient, trial):
    """Return (is_eligible: bool, reason: str)."""
    age = patient["metadata"]["age"]
    conds = set(patient["metadata"]["conditions"])
    c = trial["criteria"]
    
    reasons = []
    is_eligible = True
    
    # Age check
    if age < c["min_age"]:
        reasons.append(f"Age {age} below minimum {c['min_age']}")
        is_eligible = False
    elif age > c["max_age"]:
        reasons.append(f"Age {age} above maximum {c['max_age']}")
        is_eligible = False
    else:
        reasons.append(f"Age {age} within [{c['min_age']}-{c['max_age']}]")
    
    # Required conditions
    required = set(c["required_conditions"])
    missing = required - conds
    if missing:
        reasons.append(f"Missing required: {', '.join(sorted(missing))}")
        is_eligible = False
    elif required:
        reasons.append(f"Has required: {', '.join(sorted(required))}")
    
    # Excluded conditions
    excluded = set(c["excluded_conditions"])
    has_excluded = excluded & conds
    if has_excluded:
        reasons.append(f"Has excluded: {', '.join(sorted(has_excluded))}")
        is_eligible = False
    elif excluded:
        reasons.append(f"None of excluded conditions present")
    
    return is_eligible, "; ".join(reasons)


def generate_patient_for_trial(pid, trial, target_eligible=True):
    """Generate a patient biased toward being eligible or not for a specific trial."""
    c = trial["criteria"]
    
    if target_eligible:
        # Age within range
        age = random.randint(c["min_age"], c["max_age"])
        # Must have required conditions
        conditions = set(c["required_conditions"])
        # Add some extra conditions (but avoid excluded ones)
        extras = [x for x in ALL_CONDITIONS 
                  if x not in conditions and x not in c["excluded_conditions"]]
        if extras and random.random() < 0.5:
            conditions.add(random.choice(extras))
    else:
        # Randomly pick a way to be ineligible
        strategy = random.choice(["age_low", "age_high", "missing_required", "has_excluded"])
        
        if strategy == "age_low" and c["min_age"] > 18:
            age = random.randint(18, c["min_age"] - 1)
            conditions = set(c["required_conditions"])
        elif strategy == "age_high" and c["max_age"] < 85:
            age = random.randint(c["max_age"] + 1, 85)
            conditions = set(c["required_conditions"])
        elif strategy == "missing_required" and c["required_conditions"]:
            age = random.randint(c["min_age"], c["max_age"])
            # Deliberately omit required conditions
            conditions = set()
            extras = [x for x in ALL_CONDITIONS if x not in c["required_conditions"]]
            if extras:
                conditions.add(random.choice(extras))
        else:  # has_excluded
            age = random.randint(c["min_age"], c["max_age"])
            conditions = set(c["required_conditions"])
            if c["excluded_conditions"]:
                conditions.add(random.choice(c["excluded_conditions"]))
            else:
                # No excluded conditions defined; fall back to age strategy
                if c["max_age"] < 85:
                    age = random.randint(c["max_age"] + 1, 85)
                elif c["min_age"] > 18:
                    age = random.randint(18, c["min_age"] - 1)
    
    gender = random.choice(["male", "female"])
    conditions = list(conditions)
    
    negated = random.sample(
        [x for x in ALL_CONDITIONS if x not in conditions],
        min(random.randint(0, 2), len([x for x in ALL_CONDITIONS if x not in conditions]))
    )
    
    templates = [
        "Patient is a {age}-year-old {gender} with {conds}.",
        "A {age}-year-old {gender} diagnosed with {conds}.",
        "{age}-year-old {gender} patient with a history of {conds}."
    ]
    
    conds_text = " and ".join(conditions) if conditions else "no significant conditions"
    raw_text = random.choice(templates).format(age=age, gender=gender, conds=conds_text)
    
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
            "source": "balanced_global_v1"
        }
    }


def generate_random_patient(pid):
    """Generate a fully random patient (unbiased)."""
    age = random.randint(18, 85)
    gender = random.choice(["male", "female"])
    
    conditions = set()
    conditions.add(random.choice(CHRONIC_CONDITIONS))
    if random.random() < 0.5:
        conditions.add(random.choice(MENTAL_HEALTH))
    if random.random() < 0.3:
        conditions.add(random.choice(SYMPTOMS_ACUTE))
    
    conditions = list(conditions)
    
    negated = random.sample(
        [x for x in ALL_CONDITIONS if x not in conditions],
        min(random.randint(0, 2), len([x for x in ALL_CONDITIONS if x not in conditions]))
    )
    
    templates = [
        "Patient is a {age}-year-old {gender} with {conds}.",
        "A {age}-year-old {gender} diagnosed with {conds}.",
        "{age}-year-old {gender} patient with a history of {conds}."
    ]
    
    raw_text = random.choice(templates).format(
        age=age, gender=gender, conds=" and ".join(conditions)
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
            "source": "balanced_global_v1"
        }
    }


# ================= MAIN =================
def main():
    # Load trials
    trials = [json.load(open(f)) for f in sorted(TRIAL_DIR.glob("*.json"))]
    print(f"Loaded {len(trials)} trials")
    
    # Track global counts
    total_eligible = 0
    total_not_eligible = 0
    patient_counter = 0
    
    # Per-trial tracking
    trial_stats = {t["trial_id"]: {"eligible": 0, "not_eligible": 0} for t in trials}
    
    # Strategy: iterate until we hit global targets
    while (total_eligible < TARGET_ELIGIBLE or total_not_eligible < TARGET_NOT_ELIGIBLE) and patient_counter < MAX_PATIENTS:
        
        # Decide which label we need more of
        need_eligible = total_eligible < TARGET_ELIGIBLE
        need_not_eligible = total_not_eligible < TARGET_NOT_ELIGIBLE
        
        # Pick a random trial to focus on
        trial = random.choice(trials)
        
        # Generate patient biased toward what we need
        pid = f"P_BAL_{patient_counter:05d}"
        
        if need_eligible and not need_not_eligible:
            patient = generate_patient_for_trial(pid, trial, target_eligible=True)
        elif need_not_eligible and not need_eligible:
            patient = generate_patient_for_trial(pid, trial, target_eligible=False)
        else:
            # Need both; alternate or random
            target = random.choice([True, False])
            patient = generate_patient_for_trial(pid, trial, target_eligible=target)
        
        # Save patient
        with open(PATIENT_DIR / f"{pid}.json", "w") as f:
            json.dump(patient, f, indent=2)
        
        # Evaluate against ALL trials and save pairs
        for t in trials:
            is_elig, reason = get_eligibility_reason(patient, t)
            label = 1 if is_elig else 0
            
            # Check if we still need this label
            if label == 1 and total_eligible >= TARGET_ELIGIBLE:
                continue  # skip this pair
            if label == 0 and total_not_eligible >= TARGET_NOT_ELIGIBLE:
                continue  # skip this pair
            
            pair = {
                "pair_id": f"{pid}_{t['trial_id']}",
                "patient_id": pid,
                "trial_id": t["trial_id"],
                "label": label,
                "reason": reason
            }
            
            with open(PAIR_DIR / f"{pair['pair_id']}.json", "w") as f:
                json.dump(pair, f, indent=2)
            
            if label == 1:
                total_eligible += 1
                trial_stats[t["trial_id"]]["eligible"] += 1
            else:
                total_not_eligible += 1
                trial_stats[t["trial_id"]]["not_eligible"] += 1
        
        patient_counter += 1
        
        # Progress every 100 patients
        if patient_counter % 100 == 0:
            print(f"  Generated {patient_counter} patients | Eligible: {total_eligible}, Not Eligible: {total_not_eligible}")
    
    # Summary
    print("\n" + "=" * 50)
    print("✅ Balanced dataset generation complete")
    print("=" * 50)
    print(f"Patients generated: {patient_counter}")
    print(f"Total eligible pairs: {total_eligible}")
    print(f"Total not-eligible pairs: {total_not_eligible}")
    print(f"Balance ratio: {total_eligible / max(1, total_eligible + total_not_eligible):.2%} eligible")
    
    print("\nPer-trial breakdown:")
    for tid, stats in trial_stats.items():
        print(f"  {tid}: Eligible={stats['eligible']}, Not Eligible={stats['not_eligible']}")
    
    # Save summary
    summary = {
        "patients_generated": patient_counter,
        "total_eligible": total_eligible,
        "total_not_eligible": total_not_eligible,
        "per_trial": trial_stats
    }
    with open(PAIR_DIR / "generation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n📄 Summary saved to {PAIR_DIR / 'generation_summary.json'}")


if __name__ == "__main__":
    main()
