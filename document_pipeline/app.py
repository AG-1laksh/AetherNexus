import os

# Silence Intel MKL/OpenMP duplicate library runtime conflicts on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import uuid
import json
from typing import Optional, List, Any, Union
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import UPLOAD_DIR, OUTPUT_JSON_DIR
from utils.json_export import ExportedDocument, ExportedDocumentAPI
from utils.status import get_status, update_status

import asyncio
from concurrent.futures import ProcessPoolExecutor

from utils.logger import setup_logger

logger = setup_logger(__name__)

app = FastAPI(
    title="Document Intelligence Pipeline",
    description="Industrial Knowledge Intelligence Platform — document ingestion, OCR, chunking, entity extraction, and vector storage.",
    version="0.1.0",
)

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

process_pool = None

@app.on_event("startup")
def startup_event():
    global process_pool
    # Limit max_workers to prevent out-of-memory on heavy ML models
    process_pool = ProcessPoolExecutor(max_workers=2)
    logger.info("Started ProcessPoolExecutor")

@app.on_event("shutdown")
def shutdown_event():
    global process_pool
    if process_pool:
        process_pool.shutdown(wait=True)
        logger.info("Shut down ProcessPoolExecutor")

async def pipeline_wrapper(document_id: str, filepath: str, filename: str):
    # Initial status is written here so the API immediately knows it's queued
    update_status(document_id, "processing", current_stage="queued")
    loop = asyncio.get_running_loop()
    try:
        # Import inside the wrapper to prevent multiprocess fork-bomb imports on Windows
        from pipeline import run_pipeline_task_subprocess
        await loop.run_in_executor(process_pool, run_pipeline_task_subprocess, document_id, filepath, filename)
        # Success status is handled by the worker process
    except Exception as e:
        logger.error(f"Background process failed for {document_id}: {e}")
        update_status(document_id, "failed", error=str(e))

# --- Pydantic Models ---

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str

class ProcessRequest(BaseModel):
    document_id: str

class ProcessResponse(BaseModel):
    document_id: str
    status: str

class DocumentStatusResponseSlim(BaseModel):
    status: str
    current_stage: Optional[str] = None
    error: Optional[str] = None
    result: Optional[ExportedDocumentAPI] = None

class DocumentStatusResponseFull(BaseModel):
    status: str
    current_stage: Optional[str] = None
    error: Optional[str] = None
    result: Optional[ExportedDocument] = None



# --- Endpoints ---

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness / readiness probe."""
    return {"status": "ok"}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Accepts multipart file upload and saves to disk."""
    allowed_extensions = {".pdf", ".docx", ".xlsx", ".xls", ".png", ".jpg", ".jpeg"}
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    
    if ext not in allowed_extensions:
        logger.warning(f"Upload rejected: unsupported file type {ext}")
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {ext}")
        
    document_id = str(uuid.uuid4())
    safe_filename = f"{document_id}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"File uploaded successfully: {safe_filename}")
    except Exception as e:
        logger.error(f"Failed to save uploaded file {safe_filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
        
    return UploadResponse(
        document_id=document_id,
        filename=file.filename or "unknown",
        status="uploaded"
    )

@app.post("/process", response_model=ProcessResponse)
async def process_document(request: ProcessRequest, background_tasks: BackgroundTasks):
    """Triggers the async processing pipeline for an uploaded document."""
    doc_id = request.document_id
    
    # Locate the file in UPLOAD_DIR
    matched_files = list(UPLOAD_DIR.glob(f"{doc_id}_*"))
    if not matched_files:
        logger.warning(f"Process request failed: Document ID {doc_id} not found in uploads.")
        raise HTTPException(status_code=404, detail="Document ID not found in uploads.")
        
    filepath = matched_files[0]
    original_filename = filepath.name.replace(f"{doc_id}_", "", 1)
    
    # Spawn background task in the ProcessPoolExecutor via the wrapper
    background_tasks.add_task(pipeline_wrapper, doc_id, str(filepath), original_filename)
    logger.info(f"Enqueued background process task for {doc_id}")
    
    return ProcessResponse(
        document_id=doc_id,
        status="processing"
    )

@app.get("/document/{id}", response_model=Union[DocumentStatusResponseFull, DocumentStatusResponseSlim])
async def get_document_status(id: str, include_embeddings: bool = False):
    """Checks the status of a document job and returns JSON payload if completed."""
    
    status_info = get_status(id)
    if status_info is None:
        raise HTTPException(status_code=404, detail="Document job not found.")
        
    status = status_info.get("status", "processing")
    current_stage = status_info.get("current_stage")
    error = status_info.get("error")

    if status == "completed":
        json_path = OUTPUT_JSON_DIR / f"{id}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if include_embeddings:
                return DocumentStatusResponseFull(status="completed", current_stage=current_stage, result=data)
            else:
                return DocumentStatusResponseSlim(status="completed", current_stage=current_stage, result=data)

    return DocumentStatusResponseSlim(status=status, current_stage=current_stage, error=error)
