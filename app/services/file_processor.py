import pdfplumber
from fastapi import UploadFile

from app.services.embedding import create_embedding
from app.services.vector_store import VectorStore


class FileProcessor:
	def __init__(self) -> None:
		self.processed_files: list[str] = []
		self.failed_files: list[str] = []
		self.chunks_created = 0

	@staticmethod
	def validate_file(file: UploadFile) -> bool:
		# TODO add validations
		return True

	@staticmethod
	def process_pdf(file: UploadFile) -> list[str]:
		# TODO improve chunking strategy
		# TODO add support for scanned PDFs with OCR
		chunks = []
		with pdfplumber.open(file.file) as pdf:  # type: ignore[arg-type]
			for page in pdf.pages:
				text = page.extract_text()
				if text:
					chunks.append(text)
		embeddings = [create_embedding(chunk) for chunk in chunks]
		vector_store = VectorStore()
		vector_store.store_embeddings(chunks, embeddings)
		return chunks

	def process_files(self, files: list[UploadFile]) -> None:
		if not files:
			raise ValueError("No files provided.")
		for file in files:
			if not self.validate_file(file):
				self.failed_files.append(file.filename) if file.filename else None
				continue
			# TODO add error handling for file processing
			result = self.process_pdf(file)
			self.chunks_created += len(result)
			self.processed_files.append(file.filename) if file.filename else None
