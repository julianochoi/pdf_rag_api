from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.services.file_processor import FileProcessor

router = APIRouter(tags=["documents"])


class UploadedFileResponse(BaseModel):
	message: str
	documents_indexed: int
	total_chunks: int


# TODO make sure this endpoint does not block the application event loop when processing large files
@router.post("/documents", status_code=200)
def upload_documents(files: list[UploadFile]) -> UploadedFileResponse:
	"""
	Upload documents to be processed and indexed.
	- **files**: List of files to be processed.
	"""
	if not files:
		raise HTTPException(status_code=400, detail="No files provided.")
	try:
		processor = FileProcessor()
		processor.process_files(files)
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

	message = "Documents processed successfully"
	# NOTE should we fail for all files if one fails?
	if processor.failed_files:
		message = f"Documents processed with errors. Failed files: {', '.join(processor.failed_files)}"

	return UploadedFileResponse(
		message=message,
		documents_indexed=len(processor.processed_files),
		total_chunks=processor.chunks_created,
	)
