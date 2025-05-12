from fastapi import APIRouter, HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel

from app.services import vector_store
from app.services.file_processor import FileLoader

router = APIRouter(tags=["documents"])


class UploadedFileResponse(BaseModel):
	message: str
	documents_indexed: int
	total_chunks: int


@router.post("/documents", status_code=200)
def upload_documents(files: list[UploadFile]) -> UploadedFileResponse:
	"""
	Upload documents to be processed and indexed.
	- **files**: List of files to be processed.
	"""
	if not files:
		raise HTTPException(status_code=400, detail="No files provided.")
	try:
		processor = FileLoader()
		processor.process_files(files)
	except Exception:
		logger.exception("Error processing files")
		raise HTTPException(status_code=500, detail="Error processing files.")

	message = "Documents processed successfully"
	# NOTE should we fail for all files if one fails?
	if processor.failed_files:
		message = f"Documents processed with errors. Failed files: {', '.join(processor.failed_files)}"

	return UploadedFileResponse(
		message=message,
		documents_indexed=len(processor.processed_files),
		total_chunks=processor.chunks_created,
	)


@router.delete("/documents", status_code=201)
def delete_documents() -> dict[str, str]:
	vector_store.VectorStore().reset_collection()
	return {"message": "All documents deleted from the index."}
