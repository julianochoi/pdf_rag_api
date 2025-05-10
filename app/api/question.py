from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import llm
from app.services.vector_store import VectorStore

router = APIRouter(tags=["question"])


class QuestionRequest(BaseModel):
	question: str


class QuestionResponse(BaseModel):
	answer: str | list[str | dict[Any, Any]]
	chunks: list[str]


@router.post("/question")
def ask_question(payload: QuestionRequest) -> QuestionResponse:
	vector_store = VectorStore()
	retrieved_chunks = vector_store.retrieve_relevant_chunks(payload.question)
	answer = llm.answer_question(payload.question, retrieved_chunks)
	return QuestionResponse(
		answer=answer.content,
		chunks=retrieved_chunks,
	)
