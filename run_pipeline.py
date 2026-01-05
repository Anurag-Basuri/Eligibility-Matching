import pickle
from pathlib import Path
from src.utils.balancer import balance_pairs

# ===============================
# IMPORT PROJECT MODULES
# ===============================
from src.utils.json_loader import load_all_data
from src.privacy.anonymizer import anonymize
from src.preprocessing import preprocess
from src.features.tfidf_vectorizer import TFIDFVectorizer
from src.models.train_classifier import train_and_evaluate


# ===============================
# MAIN PIPELINE
# ===============================
def main():
    print("\n========== CLINICAL TRIAL MATCHING PIPELINE ==========\n")

    # ---------------------------
    # Load data
    # ---------------------------
    print("🔹 Loading data...")
    patients, trials, pairs = load_all_data()

    print(f"Patients loaded : {len(patients)}")
    print(f"Trials loaded   : {len(trials)}")
    print(f"Pairs loaded    : {len(pairs)}")

    # Build lookup maps
    patient_map = {p["patient_id"]: p for p in patients}
    trial_map = {t["trial_id"]: t for t in trials}

    texts = []
    labels = []
    skipped = 0

    # ---------------------------
    # Build training samples
    # ---------------------------
    print("\n🔹 Preparing training samples...")

    for pair in pairs:
        patient = patient_map.get(pair["patient_id"])
        trial = trial_map.get(pair["trial_id"])

        if patient is None or trial is None:
            skipped += 1
            continue

        # Runtime anonymization (privacy enforcement)
        anon_text = anonymize(patient["raw_text"])

        # Combine patient + trial text
        combined_text = f"{anon_text} {trial['eligibility_text']}"

        # Preprocess
        processed_text = preprocess(combined_text)

        texts.append(processed_text)
        labels.append(pair["label"])

    print(f"✅ Valid samples used : {len(texts)}")
    print(f"⚠️ Skipped pairs      : {skipped}")

    if not texts:
        raise RuntimeError("No valid samples found. Pipeline cannot continue.")
    
    print("\n🔹 Balancing dataset at pair level...")

    texts, labels = balance_pairs(texts, labels)

    print(f"Balanced samples: {len(labels)}")
    print(f"Eligible ratio: {sum(labels)/len(labels):.2%}")

    # ---------------------------
    # TF-IDF Vectorization
    # ---------------------------
    print("\n🔹 Vectorizing text with TF-IDF...")

    vectorizer = TFIDFVectorizer(
        ngram_range=(1, 2),
        max_features=5000
    )

    X = vectorizer.fit_transform(texts)

    print("✅ TF-IDF complete")
    print("Feature matrix shape:", X.shape)

    # Save vectorizer
    Path("models").mkdir(exist_ok=True)
    vectorizer.save("models/tfidf.pkl")
    print("💾 TF-IDF vectorizer saved")

    # ---------------------------
    # Train & evaluate models
    # ---------------------------
    print("\n🔹 Training and evaluating classifiers...")

    results = train_and_evaluate(X, labels)

    for name, res in results.items():
        print(f"\n📊 MODEL: {name.upper()}")
        print(f"Accuracy : {res['accuracy']:.4f}")
        print(f"Precision: {res['precision']:.4f}")
        print(f"Recall   : {res['recall']:.4f}")
        print(f"F1-score : {res['f1']:.4f}")
        print("Confusion Matrix:")
        print(res["confusion_matrix"])

    # ---------------------------
    # Save best model
    # ---------------------------
    best_model_name = max(results, key=lambda k: results[k]["f1"])
    best_model = results[best_model_name]["model"]

    with open("models/classifier.pkl", "wb") as f:
        pickle.dump(best_model, f)

    print(f"\n💾 Best model saved: {best_model_name}")
    print("\n========== PIPELINE COMPLETE ==========\n")


# ===============================
# ENTRY POINT
# ===============================
if __name__ == "__main__":
    main()
