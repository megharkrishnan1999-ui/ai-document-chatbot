from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document_processor import extract_text_from_pdf
from app.services.text_chunker import chunk_text
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import (
    add_documents,
    get_all_documents,
    delete_document,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if file.content_type != "application/pdf":

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_path = UPLOAD_DIR / file.filename

    # 1. Save PDF
    with file_path.open("wb") as buffer:

        while chunk := await file.read(
            1024 * 1024
        ):
            buffer.write(chunk)

    # 2. Extract text
    text = extract_text_from_pdf(
        str(file_path)
    )

    # 3. Split into chunks
    chunks = chunk_text(text)

    if not chunks:

        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from the PDF.",
        )

    # 4. Generate embeddings
    embeddings = generate_embeddings(
        chunks
    )

    # 5. Create IDs
    ids = [
        f"{file.filename}_{index}"
        for index in range(len(chunks))
    ]

    # 6. Create metadata
    metadatas = [

        {
            "filename": file.filename,
            "chunk_id": index,
        }

        for index in range(len(chunks))
    ]

    # 7. Store in ChromaDB
    add_documents(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return {

        "filename": file.filename,

        "content_type": file.content_type,

        "message":
            "File uploaded and processed successfully",

        "text_length": len(text),

        "chunk_count": len(chunks),
    }


# ==========================================
# GET ALL UPLOADED DOCUMENTS
# ==========================================

@router.get("")
def list_documents():

    results = get_all_documents()

    metadatas = results.get(
        "metadatas",
        []
    )

    documents = {}

    for metadata in metadatas:

        filename = metadata.get(
            "filename"
        )

        if filename not in documents:

            documents[filename] = {
                "filename": filename,
                "chunk_count": 0,
            }

        documents[filename][
            "chunk_count"
        ] += 1

    # Add actual PDF file information
    for document in documents.values():

        file_path = (
            UPLOAD_DIR /
            document["filename"]
        )

        document["exists"] = (
            file_path.exists()
        )

    return {
        "documents":
            list(documents.values())
    }


# ==========================================
# DELETE DOCUMENT
# ==========================================

@router.delete("/{filename}")
def remove_document(filename: str):

    # Delete chunks from ChromaDB
    deleted_chunks = delete_document(
        filename
    )

    # Delete actual PDF
    file_path = (
        UPLOAD_DIR /
        filename
    )

    if file_path.exists():

        file_path.unlink()

    return {

        "message":
            "Document deleted successfully",

        "filename": filename,

        "deleted_chunks":
            deleted_chunks,
    }