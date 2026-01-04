import json
import random
import os
import re
import argparse
from collections import Counter
from datetime import datetime
from pathlib import Path

# CONFIG
BASE_DIR = Path("data")
PATIENT_DIR = BASE_DIR / "patients"
TRIAL_DIR = BASE_DIR / "trials"
PAIR_DIR = BASE_DIR / "pairs"

NUM_SYNTHETIC_PATIENTS = 150

# Sample pool of medical conditions(unique, diverse)
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
    "infertility",
    "sleep apnea",
    "GERD",
    "IBS",
    "diverticulitis",
    "chronic fatigue syndrome",
    "fibromyalgia",
    "bipolar disorder",
    "schizophrenia",
    "PTSD",
    "OCD",
    "borderline personality disorder",
    "substance use disorder",
    "alcoholism",
    "smoking",
    "drug addiction",
]

# Ensure directories exist
os.makedirs(PATIENT_DIR, exist_ok=True)
os.makedirs(TRIAL_DIR, exist_ok=True)
os.makedirs(PAIR_DIR, exist_ok=True)

# SAMPLE DATA (names)
MALE_NAMES = [
    "Raj Kumar", "Aarav Sharma", "Sourav Patel", "Nikhil Singh", "Rohan Mehta",
    "Deepak Gupta", "Vikram Rao", "Sanjay Verma", "Arjun Joshi", "Karan Dhillon", "Nitin Chauhan", "Manish Malhotra", "Amitabh Tiwari", "Rakesh Yadav", "Suresh Nair", "Vijay Desai", "Harish Iyer", "Pranav Sinha", "Aditya Ghosh", "Siddharth Chatterjee"
]

FEMALE_NAMES = [
    "Ankita Sharma", "Wei Ling", "Fatima Khan", "Priya Nair", "Kavita Rao",
    "Sneha Iyer", "Meera Menon", "Aisha Siddiqui", "Lakshmi Reddy", "Divya Kapoor", "Sunita Joshi", "Pooja Verma", "Rina Patel", "Nisha Gupta", "Lata Singh", "Zara Ali", "Maya Das", "Sana Sheikh", "Tina Fernandes", "Ritu Chatterjee"
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

# PATIENT GENERATION
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

# ELIGIBILITY CHECK
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
    parser.add_argument("--visualize", action="store_true", help="Create simple visualizations (age histogram, condition counts)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output while generating")
    return parser.parse_args()


def main():
    args = parse_args()
    num = args.num
    batch = args.batch or datetime.now().strftime("%Y%m%d%H%M%S")
    visualize = args.visualize
    verbose = args.verbose

    # Stats collectors for summary & visualization
    ages = []
    cond_counter = Counter()
    trial_eligible = Counter()
    total_pairs = 0
    eligible_pairs = 0

    # Generate patients and pairs for this batch
    for i in range(num):
        pid = f"P_SYN_{batch}_{i+1:03d}"
        patient = generate_patient(pid)

        patient_path = PATIENT_DIR / f"{pid}.json"
        with open(patient_path, "w") as f:
            json.dump(patient, f, indent=2)

        ages.append(patient["metadata"]["age"])
        for c in patient["metadata"]["conditions"]:
            cond_counter[c] += 1

        if args.skip_pairs:
            continue

        for trial in trials:
            label = int(is_eligible(patient, trial))
            total_pairs += 1
            eligible_pairs += label
            trial_eligible[trial["trial_id"]] += label

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

        if verbose:
            print(f"[{i+1}/{num}] Generated {pid}: age={patient['metadata']['age']} gender={patient['metadata']['gender']} conditions={patient['metadata']['conditions']} pairs_created={len(trials)}")

        # periodic progress
        if (i + 1) % max(1, num // 10) == 0:
            print(f"Progress: {i+1}/{num} patients generated (batch={batch})")

    # Summary
    summary = {
        "batch": batch,
        "patients_generated": num,
        "total_pairs": total_pairs,
        "eligible_pairs": eligible_pairs,
        "eligible_rate": eligible_pairs / total_pairs if total_pairs else 0.0,
        "trial_eligible_counts": dict(trial_eligible),
        "top_conditions": cond_counter.most_common(20)
    }

    summary_path = PAIR_DIR / f"summary_{batch}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"✅ Synthetic data generation complete. batch={batch} patients={num}")
    print(f"Summary saved to {summary_path}")

    if visualize:
        try:
            import matplotlib.pyplot as plt

            # Age histogram
            plt.figure(figsize=(8, 4))
            plt.hist(ages, bins=range(10, 91, 5), color="#4C72B0", edgecolor="black")
            plt.title(f"Age distribution (batch={batch})")
            plt.xlabel("Age")
            plt.ylabel("Count")
            age_plot = PAIR_DIR / f"age_hist_{batch}.png"
            plt.tight_layout()
            plt.savefig(age_plot)
            plt.close()

            # Top conditions
            conds, counts = zip(*cond_counter.most_common(20)) if cond_counter else ([], [])
            plt.figure(figsize=(10, 6))
            plt.barh(conds[::-1], counts[::-1], color="#55A868")
            plt.title(f"Top conditions (batch={batch})")
            plt.xlabel("Count")
            cond_plot = PAIR_DIR / f"conditions_{batch}.png"
            plt.tight_layout()
            plt.savefig(cond_plot)
            plt.close()

            # Eligible per trial
            trials_ids = list(trial_eligible.keys())
            elig_counts = [trial_eligible[t] for t in trials_ids]
            plt.figure(figsize=(8, 4))
            plt.bar(trials_ids, elig_counts, color="#C44E52")
            plt.title(f"Eligible counts per trial (batch={batch})")
            plt.xlabel("Trial ID")
            plt.ylabel("Eligible count")
            trial_plot = PAIR_DIR / f"trial_eligible_{batch}.png"
            plt.tight_layout()
            plt.savefig(trial_plot)
            plt.close()

            print(f"Visualizations saved: {age_plot}, {cond_plot}, {trial_plot}")
        except Exception as e:
            print("Visualization skipped: matplotlib not available or error occurred:", e)


if __name__ == "__main__":
    main()
