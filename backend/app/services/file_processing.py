import os
import pathlib
from typing import Iterator
from uuid import uuid4

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from fastapi import UploadFile
from langchain_core.documents import Document
from loguru import logger

from app.core.config import get_app_settings
from app.services.vector_store import VectorStore


class FileLoader:
	def __init__(self) -> None:
		settings = get_app_settings()
		# NOTE hardcoded formats for now
		allowed_formats = ["pdf", "docx"]
		self.tmp_dir = "/tmp/pdf_processing"
		self.converter = DocumentConverter(allowed_formats=allowed_formats)
		self.chunker = HybridChunker(
			tokenizer=f"sentence-transformers/{settings.embedding_model}",
			merge_peers=True,
		)
		self.processed_files_count = 0
		self.chunks_created = 0

	def yield_chunked_documents(
		self,
		filename: str | None,
		dl_doc: DoclingDocument,
	) -> Iterator[Document]:
		chunk_iter = self.chunker.chunk(dl_doc)
		for chunk in chunk_iter:
			yield Document(
				page_content=self.chunker.contextualize(chunk=chunk),
				metadata={
					"source": filename,
					"dl_meta": chunk.meta.export_json_dict(),
				},
			)

	def process_pdf(self, file_path: str, filename: str) -> int:
		"""Process a PDF file and store its embeddings.

		Returns the number of chunks created.
		"""
		logger.info(f"Processing file: {file_path}")
		vector_store = VectorStore()
		chunks_created = 0
		conv_res = self.converter.convert(source=file_path)
		logger.info(f"Chunking file: {file_path}")
		doc_iter = self.yield_chunked_documents(
			filename=filename,
			dl_doc=conv_res.document,
		)
		for doc in doc_iter:
			vector_store.collection.add(
				ids=[str(uuid4())],
				# TODO add support to normalize the document metadata
				metadatas=[{"source": filename}],
				documents=[doc.page_content],
			)
			chunks_created += 1
		logger.info(f"Processed {chunks_created} chunks from {filename}")
		return chunks_created

	def save_temp_file(self, file: UploadFile) -> str:
		random_id = str(uuid4())
		# create a temporary directory if it doesn't exist
		pathlib.Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)
		temp_file_path = f"{self.tmp_dir}/{random_id}-{file.filename}"
		with open(temp_file_path, "wb") as f:
			f.write(file.file.read())
		return temp_file_path

	def delete_temp_file(self, file_path: str) -> None:
		if os.path.exists(file_path):
			os.remove(file_path)

	def process_files(self, files: list[UploadFile]) -> None:
		logger.info("Processing files")
		if not files:
			raise ValueError("No files provided.")
		for file in files:
			try:
				file_path = self.save_temp_file(file)
				self.chunks_created += self.process_pdf(file_path, file.filename)
				self.processed_files_count += 1
			finally:
				self.delete_temp_file(file_path)
