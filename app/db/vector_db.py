from chromadb import HttpClient
from chromadb.api import ClientAPI

from app.core.config import AppSettings


def create_client(settings: AppSettings) -> ClientAPI:
	client = HttpClient(
		host=settings.chroma_host,
		port=settings.chroma_port,
	)
	client.get_or_create_collection(name=settings.chroma_collection)
	return client
