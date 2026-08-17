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

    # 3. Get distances from retrieved chunks
    distances = results["distances"][0]

    # 4. Check whether the most relevant chunk is relevant enough
    if distances[0] > 1.5:
        return {
            "question": request.question,
            "answer": "The information is not available in the document.",
            "sources": [],
            "metadata": [],
            "distances": distances,
        }

    # 5. Get retrieved chunks
    chunks = results["documents"][0]

    # 6. Combine chunks into context
    context = "\n\n".join(chunks)

    # 7. Generate answer using local LLM
    answer = generate_answer(
        question=request.question,
        context=context,
    )

    # 8. Create unique sources
    metadata = results["metadatas"][0]

    sources = []
    seen = set()

    for item in metadata:
        source_key = (
            item["filename"],
            item["chunk_id"],
        )

        if source_key not in seen:
            sources.append({
                "filename": item["filename"],
                "chunk_id": item["chunk_id"],
            })
            seen.add(source_key)

    # 9. Return final response
    return {
        "question": request.question,
        "answer": answer,
        "sources": sources,
    }