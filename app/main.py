from fastapi import FastAPI

from app.api.exception_handlers import register_exception_handlers
from app.api.router import api_router
from app.core.config import settings
from app.core.log_config import setup_logging

setup_logging(settings.LOG_LEVEL)

app = FastAPI(title="Expense Tracker")

register_exception_handlers(app)

app.include_router(api_router)
