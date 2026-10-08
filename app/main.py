from fastapi import FastAPI

from app.api.routers import health, users

app = FastAPI(title="Expense Tracker")

app.include_router(health.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
