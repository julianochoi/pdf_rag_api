from fastapi import APIRouter

from app.api import documents, question

api_router = APIRouter()
api_router.include_router(documents.router)
api_router.include_router(question.router)
