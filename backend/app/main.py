from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from celery.result import AsyncResult
from fastapi.middleware.cors import CORSMiddleware


import os
import uuid
import shutil
from .tasks import convert_to_docx  # Celery task

app = FastAPI(
    title="Text-to-DOCX Converter API",
    description="Convert text/markdown/HTML files to DOCX format",
    version="1.0.0"
)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/convert/file", summary="Upload file for conversion")
async def convert_file(file: UploadFile = File(...)):
    """Accepts TXT, MD, HTML files and returns conversion job ID"""
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in ['.txt', '.md', '.html']:
        raise HTTPException(400, "Unsupported file type")
    
    # Save uploaded file
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Start conversion task
    task = convert_to_docx.delay(input_path)
    return {"job_id": task.id}

@app.get("/convert/{job_id}/status", summary="Check conversion status")
def check_status(job_id: str):
    """Get conversion job status and result path"""
    task_result = AsyncResult(job_id)
    return {
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }

@app.get("/download", summary="Download converted file")
def download_file(job_id: str):
    """Download converted DOCX file by job ID"""
    task_result = AsyncResult(job_id)
    if not task_result.ready():
        raise HTTPException(404, "Conversion not complete")
    
    output_path = task_result.result
    if not os.path.exists(output_path):
        raise HTTPException(404, "File not found")
    
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="converted.docx"
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["*"] for all origins (less secure)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)