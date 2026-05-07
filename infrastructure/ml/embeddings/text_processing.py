import json
import os
import re
from pathlib import Path

import aiohttp
import numpy as np
from dotenv import load_dotenv
from numpy.typing import NDArray
from sentence_transformers import SentenceTransformer

from app.core.logs_config.logger_wrappers import service_logger

load_dotenv()

hf_token = os.getenv("HF_TOKEN")
if hf_token:
    os.environ["HF_TOKEN"] = hf_token


class TextProcessing:
    def __init__(
        self,
        cat_examples: dict[str, list[str]],
        file_name_to_cache: str = "embeddings",
        threshold: float = 0.2,
    ):
        self.threshold = threshold
        self.localai_url = os.getenv("LOCALAI_HOST")
        self.file_path_to_cache = Path(__file__).parent / file_name_to_cache

        self._init_bert_hash(cat_examples, self.file_path_to_cache)

    def _init_bert_hash(
        self, cat_examples: dict[str, list[str]], file_path_to_cache: Path
    ) -> None:
        model_name = "neuml/bert-hash-nano-embeddings"
        self.embd_model = SentenceTransformer(
            model_name_or_path=model_name, trust_remote_code=True
        )

        self._cat_embeddings = {}
        embedding_path = file_path_to_cache.with_suffix(".bert_hash.npy")
        metadata_path = file_path_to_cache.with_suffix(".bert_hash.json")

        if embedding_path.exists() and metadata_path.exists():
            embeddings = np.load(embedding_path)

            with open(metadata_path, "r", encoding="utf-8") as file:
                metadata = json.load(file)

            for index, category in enumerate(metadata["categories"]):
                self._cat_embeddings[category] = embeddings[index]
        else:
            for cat_name, phrases in cat_examples.items():
                category_embedding = self._calc_embeddings(phrases)
                self._cat_embeddings[cat_name] = category_embedding
            self._save_embeddings_and_meta(file_path_to_cache)

    def _calc_embeddings(self, phrases: list[str]) -> NDArray[np.float32]:
        embeddings = self.embd_model.encode(phrases, convert_to_numpy=True)
        return np.mean(embeddings, axis=0)

    def _save_embeddings_and_meta(self, file_name_to_cache: Path):
        categories = list(self._cat_embeddings.keys())
        embeddings = np.array(list(self._cat_embeddings.values()))

        metadata = {
            "categories": categories,
            "num_categories": len(categories),
        }

        with open(
            f"{file_name_to_cache}.bert_hash.json", "w", encoding="utf-8"
        ) as file:
            json.dump(metadata, file, indent=2, ensure_ascii=False)

        np.save(f"{file_name_to_cache}.bert_hash.npy", embeddings)

    def _cosine_similarity(self, vector1, vector2) -> float:
        return np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        ) 
    @service_logger
    def classifier(self, text: str):
        text_vec = self.embd_model.encode(text, convert_to_numpy=True)

        best_cat = None
        best_score = float("-inf")

        for cat, embedding in self._cat_embeddings.items():
            score = self._cosine_similarity(text_vec, embedding)

            if score > best_score:
                best_cat = cat
                best_score = score

        return best_cat, best_score

        # return self._localai_classifier()

    async def _localai_classifier(self, text: str):
        prompt = f"""
        Определи категорию транзакции. Варианты: {", ".join(list(self._cat_embeddings.keys()))}
        Текст: "{text}"
        Категория
        """

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.localai_url}/v1/completions",
                    json={
                        "model": "category-classifier",
                        "prompt": prompt,
                        "max_tokens": 10,
                        "temperature": 0,
                    },
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        category = data["choices"][0]["text"].strip().lower()
                        return category, 0.99
                    return "другое", 0.5
            except Exception:
                return "другое", 0.5

    async def classifier(self, text: str):
        text_vec = self.embd_model.encode(text, convert_to_numpy=True)

        best_cat = None
        best_score = float("-inf")

        for cat, embedding in self._cat_embeddings.items():
            score = self._cosine_similarity(text_vec, embedding)

            if score > best_score:
                best_cat = cat
                best_score = score

        if best_score >= self.threshold:
            return best_cat, best_score

        return await self._localai_classifier()

    def extract_amount(self, input_text: str) -> float | None:
        input_text = input_text.lower()

        number_pattern = r"(\d+[.,]?\d*)"
        patterns = [
            rf"{number_pattern}\s*(?:р|руб|byn|\$)?",
            rf"(?:за|стоимость|цена)\s+{number_pattern}",
            number_pattern,
        ]
        for pattern in patterns:
            match = re.search(pattern=pattern, string=input_text)
            if match:
                return float(match.group(1).replace(",", "."))

        return None
