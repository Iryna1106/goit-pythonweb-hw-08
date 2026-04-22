import uvicorn
from fastapi import FastAPI

from src.api.contacts import router as contacts_router
from src.conf.config import settings

app = FastAPI(
    title="Contacts REST API",
    description="REST API для зберігання та управління контактами (FastAPI + SQLAlchemy + PostgreSQL).",
    version="1.0.0",
)

app.include_router(contacts_router, prefix="/api")


@app.get("/", tags=["root"])
def root():
    return {"message": "Contacts REST API is running. See /docs for Swagger UI."}


@app.get("/healthz", tags=["root"])
def healthcheck():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
