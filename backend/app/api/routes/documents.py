from pathlib import Path 
#Path gives us a clean, cross-platform way of working with files and folders.

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)
#Create the uploads folder if it doesn't already exist.If it already exists, don't throw an error.
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":  #checks what type of file the client claims to have uploaded.
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    file_path = UPLOAD_DIR / file.filename

    with file_path.open("wb") as buffer: #PDFs are binary files, so we need to write them in binary mode.
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File uploaded successfully",
    }