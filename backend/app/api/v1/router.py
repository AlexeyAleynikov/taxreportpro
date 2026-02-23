"""Центральный роутер API v1."""

from fastapi import APIRouter

from app.api.v1 import auth, users, clients, tax_years, documents, calc, reports, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(tax_years.router, prefix="/tax-years", tags=["tax_years"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(calc.router, prefix="/calc", tags=["calculation"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
