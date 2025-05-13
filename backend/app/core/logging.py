# mypy: ignore-errors
import logging
import sys
from datetime import time, timedelta
from pprint import pformat

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

from app.core import config


class InterceptHandler(logging.Handler):
	def emit(self, record: logging.LogRecord):
		# Get corresponding Loguru level if it exists
		try:
			level = logger.level(record.levelname).name
		except ValueError:
			level = record.levelno

		# Find caller from where originated the logged message
		frame, depth = logging.currentframe(), 2
		while frame.f_code.co_filename == logging.__file__:
			frame = frame.f_back
			depth += 1

		logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def correlation_id_filter(record: dict) -> str:
	from asgi_correlation_id.context import correlation_id

	if "correlation_id" not in record["extra"]:
		record["extra"]["correlation_id"] = correlation_id.get()
	return record["extra"]["correlation_id"] or "N/A"


def format_record(record: dict) -> str:
	format_string = (
		"<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
		"<level>{level: <8}</level> | "
		"<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
	)
	if record["extra"].get("correlation_id") is not None:
		format_string += " [{extra[correlation_id]}]"
	format_string += " - <level>{message}</level>"
	if record["extra"].get("payload") is not None:
		record["extra"]["payload"] = pformat(record["extra"]["payload"], indent=4, compact=True, width=88)
		format_string += "\n<level>{extra[payload]}</level>"
	format_string += "{exception}\n"
	return format_string


def init_logging(
	filename: str,
	settings: config.AppSettings,
	rotation: int | timedelta | time | str = "100 MB",
):
	# intercept everything at the root logger
	logging.root.handlers = [InterceptHandler()]

	log_level = settings.log_level.upper()
	logging.root.setLevel(log_level)

	# remove every other logger's handlers and propagate to root logger
	for name in logging.root.manager.loggerDict.keys():
		logging.getLogger(name).handlers = []
		logging.getLogger(name).propagate = True

	# Suppress httpx INFO messages
	logging.getLogger("httpx").setLevel(logging.WARNING)

	# configure loguru
	handlers = [
		{
			"sink": sys.stdout,
			"level": log_level,
			"format": format_record,
			"filter": correlation_id_filter,
		},
		{
			"sink": f"./logs/{filename}",
			"level": log_level,
			"format": format_record,
			"filter": correlation_id_filter,
			"rotation": rotation,
			"mode": "a",  # append
		},
		# TODO add sink to stream handler
	]
	logger.configure(handlers=handlers)
