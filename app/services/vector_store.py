from app.core.config import AppSettings, get_app_settings
from app.db import vector_db
from app.services import embedding


class VectorStore:
	"""Vector store for storing and retrieving embeddings."""

	def __init__(self, settings: AppSettings | None = None) -> None:
		if settings is None:
			settings = get_app_settings()
		self.client = vector_db.create_client(settings)
		self.collection = self.client.get_collection(name=settings.chroma_collection)

	def store_embeddings(self, chunks: list[str], embeddings: list[embedding.Embedding]) -> None:
		self.collection.add(
			documents=chunks,
			embeddings=embeddings,  # type: ignore
			metadatas=[{"source": chunk} for chunk in chunks],
			ids=[f"chunk_{i}" for i in range(len(chunks))],
		)

	def retrieve_relevant_chunks(self, question: str) -> list[str]:
		question_embedding = embedding.create_embedding(question)
		query = self.collection.query(
			query_embeddings=[question_embedding],  # type: ignore
			n_results=5,
		)
		docs = query["documents"]
		if not docs:
			return []
		print("docs:", docs)
		return docs[0]
