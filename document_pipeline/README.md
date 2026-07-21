# Document Intelligence Pipeline

This is an Industrial Knowledge Intelligence Platform for document ingestion, OCR, chunking, entity extraction, and vector storage.

## Running the Server

To start the FastAPI server for local development, use:

```bash
uvicorn app:app --reload --reload-exclude "uploads/*" --reload-exclude "output/*"
```

> **WARNING**: For any real processing run (not just editing code), prefer running **WITHOUT** `--reload` entirely. Even excluding folders doesn't fully eliminate the risk of the server restarting if you edit source files while a background job is mid-flight. A restart will abruptly kill the active processing job.

## Processing Time Expectations

This pipeline utilizes heavy Machine Learning models (like PaddleOCR, Spacy, and HuggingFace SentenceTransformers). Because it relies on CPU-only ML inference without GPU acceleration, **processing takes time**:
- Expect ~10-30 seconds per page on CPU.
- Large scanned PDFs may take several minutes to complete. 
This is expected behavior and not a freeze or a bug. You can poll the `/document/{id}` endpoint to observe the job's `current_stage` progressing from `parsing` to `chunking`, `entity_extraction`, `exporting`, etc.

## Optional Dependencies (ChromaDB)

The local semantic search vector database (`chromadb`) is an **optional** dependency for local development. 
- **Windows Users**: Installing `chromadb` requires Microsoft C++ Build Tools (specifically for compiling its `hnswlib` dependency). You can download the official installer [here](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
- The application works fully without it. The JSON export path and processing pipeline will complete successfully even if ChromaDB is not installed. If ChromaDB is missing, the optional `/search` endpoint will simply return a clean `503 Service Unavailable` response.
