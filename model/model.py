import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .basic_classifier import BasicClassifier


class SkClassifier(BasicClassifier):
    def __init__(self, dataset_path: str, vectorizer_path: str, model_path: str):
        self.df = pd.read_csv(dataset_path)
        self.vectorizer = joblib.load(vectorizer_path)
        self.model = joblib.load(model_path)

    def predict(self, word: str) -> tuple[str, float]:
        X = self.vectorizer.transform(["word"])  # noqa
        category = self.model.predict(X)[0]
        confidence = self.model.predict_proba(X).max()
        return category, confidence

    def retrain(self):
        vectorizer = TfidfVectorizer()
        vectorizer.transform()

        X = vectorizer.fit_transform(self.df["text"])  # noqa
        y = self.df["category"]

        model = LogisticRegression()
        model.fit(X, y)

        # joblib.dump(model, MODEL_PATH)
        # joblib.dump(vectorizer, VECTORIZER_PATH)
