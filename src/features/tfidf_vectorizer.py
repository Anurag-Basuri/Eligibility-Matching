import pickle
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer


class TFIDFVectorizer:
    # Wrapper around sklearn TfidfVectorizer for patient/trial text.

    def __init__(self, ngram_range=(1, 2), max_features=5000):
        self.vectorizer = TfidfVectorizer(
            ngram_range=ngram_range,
            max_features=max_features,
            stop_words="english",
            lowercase=True,
        )
        self._is_fitted = False

    def fit(self, texts):
        # Fit vectorizer on a list of text documents.
        self.vectorizer.fit(texts)
        self._is_fitted = True
        return self

    def transform(self, texts):
        # Transform texts to TF-IDF feature matrix.
        if not self._is_fitted:
            raise RuntimeError("Vectorizer not fitted. Call fit() first.")
        return self.vectorizer.transform(texts)

    def fit_transform(self, texts):
        # Fit and transform in one step.
        self._is_fitted = True
        return self.vectorizer.fit_transform(texts)

    def get_feature_names(self):
        # Return feature names (vocabulary terms).
        return self.vectorizer.get_feature_names_out()

    def save(self, path):
        # Save fitted vectorizer to disk.
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def load(self, path):
        # Load vectorizer from disk.
        with open(path, "rb") as f:
            self.vectorizer = pickle.load(f)
        self._is_fitted = True
        return self  # Enable chaining