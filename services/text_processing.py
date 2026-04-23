import re

import numpy as np
import pymorphy3
from sentence_transformers import SentenceTransformer


class TextProcessing:
    def __init__(self, cat_examples):
        self.morph = pymorphy3.MorphAnalyzer()
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self._cat_embeddings = {}
        self._calc_embeddings()

    def _calc_embeddings(self, category_examples: dict):
        for cat, examples in category_examples.items():
            embeddings = self.model.encode(examples)
            self._cat_embeddings[cat] = np.mean(embeddings, axis=0)

    def _cosine_similarity(self, vector1, vector2):
        return np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )

    def main_noun_searcher(self, text: str) -> list[str]:
        output = []
        for word in text.split():
            parsed_word = self.morph.parse(word)[0]
            if parsed_word.tag.POS == "NOUN":
                output.append(parsed_word.normal_form)

        return output

    def classifier(self, text: str):
        text_vec = self.model.encode([text])[0]

        best_cat = None
        best_score = 0

        for cat, embedding in self._cat_embeddings.items():
            score = self._cosine_similarity(text_vec, embedding)

            if score > best_score:
                best_cat = cat
                best_score = score

        return best_cat, best_score

    def extract_amount(self, input_text: str) -> float:
        input_text = input_text.lower()

        number_pattern = r"(\d+[.,]?\d*)"
        patterns = [
            rf"{number_pattern}\s*(?:р|руб|byn|\$)?",
            rf"(?:за|стоимость|цена)\s+{number_pattern}",
            number_pattern,
        ]
        for pattern in patterns:
            match = re.search(pattern=pattern, text=input_text)
            if match:
                return float(match.group(1).replace(",", "."))

        return None

    def keyword_search(self, text, lexicon):

    def classify_transaction(self, text: str):
        amount = self.extract_amount(text)

        cat, conf = self.classifier(text)

        if conf > 0.6:
            return cat, conf
        return None
