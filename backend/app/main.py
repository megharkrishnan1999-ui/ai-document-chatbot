from fastapi import FastAPI

from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router

app = FastAPI(
    title="AI Document Chatbot",
    description="An AI-powered chatbot that answers questions from uploaded documents.",
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(documents_router)


@app.get("/")
def root():
    return {"message": "AI Document Chatbot API is running!"}