from fastapi import APIRouter
from pydantic import BaseModel

from app.services.embedding_service import generate_embedding
from app.services.vector_store import search_documents
from app.services.llm_service import generate_answer

router = APIRouter()


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
def chat(request: ChatRequest):
    # 1. Convert user's question into an embedding
    query_embedding = generate_embedding(request.question)

    # 2. Search ChromaDB for relevant document chunks
    results = search_documents(
        query_embedding=query_embedding,
        n_results=3,
    )

    # 3. Get the retrieved chunks
    chunks = results["documents"][0]

    # 4. Combine chunks into a single context
    context = "\n\n".join(chunks)

    # 5. Ask the LLM to answer using the retrieved context
    answer = generate_answer(
        question=request.question,
        context=context,
    )

    return {
        "question": request.question,
        "answer": answer,
        "sources": chunks,
        "metadata": results["metadatas"][0],
        "distances": results["distances"][0],
    }