from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api import api_router
from app.core import config, logging, middleware
from app.services import llm, vector_store


class PdfQaAPI(FastAPI):
	settings: config.AppSettings


@asynccontextmanager
async def lifespan(app: PdfQaAPI) -> AsyncGenerator[None, None]:
	llm.build_llm_provider()
	vector_store.load_embedding_model()
	vector_store.VectorStore()
	yield


def create_app(settings: config.AppSettings | None = None) -> PdfQaAPI:
	if settings is None:
		settings = config.get_app_settings()

	app = PdfQaAPI(
		title="PDF QA API",
		description="API to handle PDF uploads and questions regarding the uploaded documents with LLM.",
		contact={"name": "Juliano Choi", "email": "julianochoi@gmail.com"},
		redoc_url=None,
		lifespan=lifespan,
	)
	app.settings = settings
	logging.init_logging("app.log", settings=settings)

	# Redirect root to docs page
	@app.get("/", include_in_schema=False)
	def docs_redirect() -> RedirectResponse:
		return RedirectResponse(url="/docs")

	middleware.define_middleware(app)
	app.include_router(api_router)
	return app


def main() -> None:
	settings = config.get_app_settings()
	in_dev_env = settings.environment.lower() != "prod"
	uvicorn.run(
		app="app.main:create_app",
		factory=True,
		host="0.0.0.0",
		port=settings.port,
		access_log=in_dev_env,
		reload=in_dev_env,
		reload_dirs="app",
		server_header=False,
	)
