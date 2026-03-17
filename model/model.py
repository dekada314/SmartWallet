import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .basic_classifier import BasicClassifier

DATASET_PATH = "SmartWallet/model/dataset.csv"
MODEL_PATH = "SmartWallet/model/dumps/model.joblib"
VECTORIZER_PATH = "SmartWallet/model/dumps/vectorizer.joblib"


class SkClassifier(BasicClassifier):
    def __init__(self):
        self.df = pd.read_csv(DATASET_PATH)
        self.vectorizer = joblib.load(VECTORIZER_PATH)
        self.model = joblib.load(MODEL_PATH)

    def predict(self, word: str) -> tuple[str, float]:
        X = self.vectorizer.transform([word])  # noqa
        category = self.model.predict(X)[0]
        confidence = self.model.predict_proba(X).max()
        return category, confidence

    def retrain(self):
        vectorizer = TfidfVectorizer()

        X = vectorizer.fit_transform(self.df["text"])  # noqa
        y = self.df["category"]

        model = LogisticRegression()
        model.fit(X, y)

        joblib.dump(model, MODEL_PATH)
        joblib.dump(vectorizer, VECTORIZER_PATH)
