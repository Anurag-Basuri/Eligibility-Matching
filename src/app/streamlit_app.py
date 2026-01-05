import sys
from pathlib import Path

# Add project root to path so 'src' imports work
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pickle

# Project imports
from src.utils.json_loader import load_all_data
from src.privacy.anonymizer import anonymize
from src.preprocessing import preprocess


# =============================
# LOAD MODELS & DATA
# =============================
@st.cache_resource
def load_models():
    models_dir = PROJECT_ROOT / "models"
    with open(models_dir / "tfidf.pkl", "rb") as f:
        vectorizer = pickle.load(f)

    with open(models_dir / "classifier.pkl", "rb") as f:
        classifier = pickle.load(f)

    return vectorizer, classifier


@st.cache_data
def load_data():
    patients, trials, _ = load_all_data(base_dir=PROJECT_ROOT / "data")
    return patients, trials


vectorizer, classifier = load_models()
patients, trials = load_data()

patient_map = {p["patient_id"]: p for p in patients}
trial_map = {t["trial_id"]: t for t in trials}


# =============================
# EXPLANATION ENGINE
# =============================
def explain_eligibility(patient, trial):
    reasons = []

    age = patient["metadata"]["age"]
    conds = set(patient["metadata"]["conditions"])
    c = trial["criteria"]

    if age < c["min_age"]:
        reasons.append(f"❌ Age {age} is below minimum {c['min_age']}")
    elif age > c["max_age"]:
        reasons.append(f"❌ Age {age} is above maximum {c['max_age']}")
    else:
        reasons.append(f"✅ Age {age} within allowed range")

    missing = set(c["required_conditions"]) - conds
    if missing:
        reasons.append(f"❌ Missing required conditions: {', '.join(missing)}")
    else:
        if c["required_conditions"]:
            reasons.append(f"✅ Required conditions satisfied")

    excluded_hit = set(c["excluded_conditions"]) & conds
    if excluded_hit:
        reasons.append(f"❌ Has excluded conditions: {', '.join(excluded_hit)}")
    else:
        if c["excluded_conditions"]:
            reasons.append("✅ No excluded conditions present")

    return reasons


# =============================
# STREAMLIT UI
# =============================
st.set_page_config(page_title="Clinical Trial Eligibility Matcher", layout="centered")

st.title("🧪 Clinical Trial Eligibility Matching")
st.write("Privacy-preserving NLP-based eligibility prediction")

st.divider()

# -----------------------------
# Selection
# -----------------------------
patient_id = st.selectbox("Select Patient", sorted(patient_map.keys()))
trial_id = st.selectbox("Select Trial", sorted(trial_map.keys()))

patient = patient_map[patient_id]
trial = trial_map[trial_id]

st.subheader("📄 Patient Summary")
st.write(patient["raw_text"])

st.subheader("📋 Trial Eligibility Criteria")
st.json(trial["criteria"])

# -----------------------------
# Prediction
# -----------------------------
if st.button("Check Eligibility"):
    anon_text = anonymize(patient["raw_text"])
    combined_text = anon_text + " " + trial["eligibility_text"]
    processed_text = preprocess(combined_text)

    X = vectorizer.transform([processed_text])

    prediction = classifier.predict(X)[0]

    if hasattr(classifier, "predict_proba"):
        score = classifier.predict_proba(X)[0][1]
    else:
        score = float(prediction)

    st.divider()
    st.subheader("🔍 Eligibility Result")

    if prediction == 1:
        st.success("✅ Eligible")
    else:
        st.error("❌ Not Eligible")

    st.metric("Eligibility Score", f"{score:.2f}")

    st.subheader("🧠 Explanation")
    explanations = explain_eligibility(patient, trial)
    for r in explanations:
        st.write(r)
