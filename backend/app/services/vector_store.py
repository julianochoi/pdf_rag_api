from functools import lru_cache

from chromadb import Collection, Documents, Embeddings, HttpClient
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from loguru import logger

from app.core.config import get_app_settings


class CustomEmbeddingFunction(embedding_functions.EmbeddingFunction[Documents]):
	"""Custom embedding function for ChromaDB."""

	def __init__(self) -> None:
		settings = get_app_settings()
		self.model = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=settings.embedding_model)

	def __call__(self, input: Documents) -> Embeddings:
		return self.model(input)

	# NOTE this is a workaround for a bug in ChromaDB
	@staticmethod
	def name() -> str:
		return "default"


@lru_cache(maxsize=1)
def load_embedding_model() -> embedding_functions.EmbeddingFunction[Documents]:
	model = CustomEmbeddingFunction()
	return model


class VectorStore:
	"""Vector store for storing and retrieving embeddings."""

	def __init__(self) -> None:
		self.settings = get_app_settings()
		self.client = HttpClient(
			host=self.settings.chroma_host,
			port=self.settings.chroma_port,
			settings=Settings(anonymized_telemetry=False),
		)
		self.collection = self._create_collection()

	def _create_collection(self) -> Collection:
		return self.client.get_or_create_collection(
			name=self.settings.chroma_collection,
			embedding_function=load_embedding_model(),  # type: ignore
		)

	def retrieve_relevant_chunks(self, question: str) -> list[str]:
		query = self.collection.query(
			query_texts=[question],
			n_results=5,
		)
		docs = query["documents"]
		if not docs:
			return []
		logger.debug(docs)
		return docs[0]

	def reset_collection(self) -> None:
		self.client.reset()
		self.colection = self._create_collection()
