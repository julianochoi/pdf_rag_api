from fastapi import APIRouter, HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel

from app.services import file_processing, vector_store

router = APIRouter(tags=["documents"])


class UploadedFileResponse(BaseModel):
	message: str
	documents_indexed: int
	total_chunks: int


# NOTE This is a CPU-intensive operation, so it could be run on the background with workers and a queue.
# NOTE This would break the user feedback loop, though, so we could use a websocket or sse to notify the user when done.
@router.post("/documents", status_code=200)
def upload_documents(files: list[UploadFile]) -> UploadedFileResponse:
	"""
	Upload documents to be processed and indexed.
	- **files**: List of files to be processed.
	"""
	try:
		processor = file_processing.FileLoader()
		processor.process_files(files)
	except Exception:
		logger.exception("Error processing files")
		raise HTTPException(status_code=500, detail="Error processing files.")

	return UploadedFileResponse(
		message="Documents processed successfully",
		documents_indexed=processor.processed_files_count,
		total_chunks=processor.chunks_created,
	)


@router.delete("/documents", status_code=201)
def delete_documents() -> dict[str, str]:
	try:
		vector_store.VectorStore().reset_collection()
		return {"message": "All documents deleted from the index."}
	except Exception:
		logger.exception("Error deleting documents")
		raise HTTPException(status_code=500, detail="Error deleting documents.")