import pickle
import importlib

class TFIDFVectorizer:
    def __init__(self):
        try:
            sklearn_text = importlib.import_module("sklearn.feature_extraction.text")
            TfidfVectorizer = getattr(sklearn_text, "TfidfVectorizer")
        except Exception as e:
            raise ImportError("scikit-learn is required to use TFIDFVectorizer; install it with 'pip install scikit-learn'") from e

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000
        )

    def fit(self, texts):
        return self.vectorizer.fit(texts)

    def transform(self, texts):
        return self.vectorizer.transform(texts)

    def save(self, path):
        with open(path, "wb") as f:
            pickle.dump(self.vectorizer, f)

    def load(self, path):
        with open(path, "rb") as f:
            self.vectorizer = pickle.load(f)
