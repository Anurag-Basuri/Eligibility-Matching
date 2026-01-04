import pickle
from sklearn.feature_extraction.text import TfidfVectorizer

class TFIDFVectorizer:
    def __init__(self):
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
