import time

from fastapi import FastAPI, Request


def define_middleware(app: FastAPI) -> None:
	# Add middleware to log request processing time
	@app.middleware("http")
	async def add_process_time_header(request: Request, call_next):
		start_time = time.perf_counter()
		response = await call_next(request)
		process_time = time.perf_counter() - start_time
		response.headers["X-Process-Time"] = str(process_time)
		# TODO send process time to logger and monitoring system
		return response
