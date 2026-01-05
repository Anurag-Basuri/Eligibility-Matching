from pathlib import Path
from src.utils.json_loader import load_all_data
from src.privacy.anonymizer import anonymize
from src.preprocessing import preprocess
from src.features.tfidf_vectorizer import TFIDFVectorizer


def main():
    print("🔹 Loading data...")
    patients, trials, pairs = load_all_data()

    print(f"Patients: {len(patients)}")
    print(f"Trials: {len(trials)}")
    print(f"Pairs: {len(pairs)}")

    # Build fast lookup maps
    patient_map = {p["patient_id"]: p for p in patients}
    trial_map = {t["trial_id"]: t for t in trials}

    texts = []
    labels = []

    skipped_pairs = 0

    print("🔹 Building training texts...")

    for pair in pairs:
        patient = patient_map.get(pair["patient_id"])
        trial = trial_map.get(pair["trial_id"])

        # Skip invalid references
        if patient is None or trial is None:
            skipped_pairs += 1
            continue

        # Runtime anonymization (privacy layer)
        anonymized_text = anonymize(patient["raw_text"])

        # Combine patient + trial text
        combined_text = anonymized_text + " " + trial["eligibility_text"]

        # Preprocess
        processed_text = preprocess(combined_text)

        texts.append(processed_text)
        labels.append(pair["label"])

    print(f"✅ Valid training samples: {len(texts)}")
    print(f"⚠️ Skipped invalid pairs: {skipped_pairs}")

    if not texts:
        raise RuntimeError("No valid training samples found. Check data integrity.")

    print("🔹 Vectorizing text with TF-IDF...")

    vectorizer = TFIDFVectorizer(
        ngram_range=(1, 2),
        max_features=5000
    )

    X = vectorizer.fit_transform(texts)

    print("✅ TF-IDF Vectorization Complete")
    print("Feature matrix shape:", X.shape)
    print("Sample labels:", labels[:10])

    # Save vectorizer
    vectorizer.save("models/tfidf.pkl")
    print("💾 TF-IDF vectorizer saved to models/tfidf.pkl")


if __name__ == "__main__":
    main()
