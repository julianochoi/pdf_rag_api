from functools import lru_cache
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from torch import Tensor

from app.core.config import get_app_settings

type Embedding = list[Tensor] | np.ndarray[Any, Any] | Tensor | dict[str, Tensor] | list[dict[str, Tensor]]


@lru_cache(maxsize=1)
def load_model() -> SentenceTransformer:
	settings = get_app_settings()
	return SentenceTransformer(settings.embedding_model)


def create_embedding(chunk: str) -> Embedding:
	model = load_model()
	embedding = model.encode(chunk, convert_to_numpy=True)
	return embedding
