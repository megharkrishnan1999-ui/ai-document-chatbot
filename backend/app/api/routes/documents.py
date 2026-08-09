from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.document_processor import extract_text_from_pdf
from app.services.text_chunker import chunk_text
router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    text = extract_text_from_pdf(str(file_path))
    chunks = chunk_text(text)
    return {
        "filename": file.filename,
    "content_type": file.content_type,
    "message": "File uploaded and processed successfully",
    "text_length": len(text),
    "chunk_count": len(chunks),
    "first_chunk": chunks[0] if chunks else "",
    }