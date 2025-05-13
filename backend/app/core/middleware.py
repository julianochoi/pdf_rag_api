import time

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import get_app_settings


def define_middlewares(app: FastAPI) -> None:
	settings = get_app_settings()
	app.add_middleware(CorrelationIdMiddleware, header_name=settings.correlation_id_header)
	app.add_middleware(
		CORSMiddleware,
		allow_origins=["*"],
		allow_methods=["*"],
		allow_headers=["X-Requested-With", settings.correlation_id_header],
		expose_headers=[settings.correlation_id_header],
	)

	# Add middleware to log request processing time
	@app.middleware("http")
	async def add_process_time_header(request: Request, call_next):
		start_time = time.perf_counter()
		response = await call_next(request)
		process_time = time.perf_counter() - start_time
		response.headers["X-Process-Time"] = str(process_time)

		correlation_id = response.headers.get(settings.correlation_id_header.lower())
		with logger.contextualize(correlation_id=correlation_id):
			logger.info(f" Request processed in {process_time:.4f} seconds")
		return response
