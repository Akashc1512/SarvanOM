from __future__ import annotations

import logging
from typing import List

from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


_model: SentenceTransformer | None = None


def get_embedder(
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
) -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading local embedding model: {model_name}")
        _model = SentenceTransformer(model_name)
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedder()
    vectors = model.encode(texts, normalize_embeddings=True, convert_to_numpy=False)
    # Ensure pure python list of lists
    return [list(map(float, v)) for v in vectors]
