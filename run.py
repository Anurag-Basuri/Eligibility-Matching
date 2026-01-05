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

    texts = []
    labels = []

    print("🔹 Building training texts...")

    for pair in pairs:
        patient = next(
            p for p in patients if p["patient_id"] == pair["patient_id"]
        )
        trial = next(
            t for t in trials if t["trial_id"] == pair["trial_id"]
        )

        # Runtime anonymization (privacy layer)
        anonymized_text = anonymize(patient["raw_text"])

        # Combine patient + trial text
        combined_text = anonymized_text + " " + trial["eligibility_text"]

        # Preprocess
        processed_text = preprocess(combined_text)

        texts.append(processed_text)
        labels.append(pair["label"])

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
