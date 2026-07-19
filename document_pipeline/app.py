import os
import uuid
import json
from typing import Optional, List, Any
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import UPLOAD_DIR, OUTPUT_JSON_DIR
from pipeline import run_pipeline_task, JOB_STATUS
from vector_db.chroma_store import LocalChromaStore
from embedding.embed import embed_text

app = FastAPI(
    title="Document Intelligence Pipeline",
    description="Industrial Knowledge Intelligence Platform — document ingestion, OCR, chunking, entity extraction, and vector storage.",
    version="0.1.0",
)

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

class DocumentStatusResponse(BaseModel):
    status: str
    result: Optional[dict] = None

class SearchResult(BaseModel):
    text: str
    metadata: dict
    score: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

# --- Endpoints ---

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness / readiness probe."""
    return {"status": "ok"}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Accepts multipart file upload and saves to disk."""
    allowed_extensions = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".jpeg"}
    ext = Path(file.filename).suffix.lower() if file.filename else ""
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {ext}")
        
    document_id = str(uuid.uuid4())
    safe_filename = f"{document_id}_{file.filename}"
    file_path = UPLOAD_DIR / safe_filename
    
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
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
        raise HTTPException(status_code=404, detail="Document ID not found in uploads.")
        
    filepath = matched_files[0]
    original_filename = filepath.name.replace(f"{doc_id}_", "", 1)
    
    # Spawn background task
    background_tasks.add_task(run_pipeline_task, doc_id, str(filepath), original_filename)
    
    return ProcessResponse(
        document_id=doc_id,
        status="processing"
    )

@app.get("/document/{id}", response_model=DocumentStatusResponse)
async def get_document_status(id: str):
    """Checks the status of a document job and returns JSON payload if completed."""
    status = JOB_STATUS.get(id, "not_found")
    
    if status == "completed":
        json_path = OUTPUT_JSON_DIR / f"{id}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return DocumentStatusResponse(status=status, result=data)
        else:
            return DocumentStatusResponse(status="completed_but_file_missing")
            
    return DocumentStatusResponse(status=status)

@app.get("/search", response_model=SearchResponse)
async def search_chunks(q: str = Query(..., description="Semantic search query"), top_k: int = Query(5)):
    """(Optional) Query local ChromaDB vector store."""
    try:
        store = LocalChromaStore()
        if not store.collection:
            raise HTTPException(status_code=503, detail="ChromaDB is not initialized.")
            
        query_embed = embed_text(q)
        results = store.query_similar(query_embed, top_k=top_k)
        
        search_results = []
        if results and results.get("documents") and results.get("distances"):
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            dists = results["distances"][0]
            
            for d, m, dist in zip(docs, metas, dists):
                search_results.append(SearchResult(
                    text=d,
                    metadata=m,
                    score=1.0 - dist # approximate cosine similarity from L2/Cosine dist
                ))
                
        return SearchResponse(results=search_results)
        
    except Exception as e:
         raise HTTPException(status_code=503, detail=f"Search failed: {e}")
