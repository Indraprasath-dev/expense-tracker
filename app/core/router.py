from fastapi import APIRouter

from app.api.routers import auth, budgets, categories, expenses, health, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(expenses.router)
api_router.include_router(budgets.router)
