from fastapi import FastAPI

from app.api.routers import health

app = FastAPI(title="Expense Tracker")

app.include_router(health.router, prefix="/api/v1")
