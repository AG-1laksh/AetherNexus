# Document Intelligence Pipeline (MVP)

An **Industrial Knowledge Intelligence Platform** that processes unstructured domain-specific documents (PDFs, Word Docs, Spreadsheets, Images), applies OCR, extracts Named Entities using NLP, embeds chunks using vector encoding, and exports strongly-typed JSON for downstream Neo4j Knowledge Graph ingestion.

## Architecture

The system operates as an asynchronous FastAPI microservice broken into distinct sequential stages:

1. **Parse & Clean**: Detects the MIME type and routes to specialized parsers (PyMuPDF, python-docx). If a PDF is scanned, it falls back to PaddleOCR. Output is cleaned by stripping arbitrary whitespace and pagination artifacts.
2. **Chunking**: Text is chunked (500-800 chars) retaining 100 char overlaps.
3. **Entity Extraction**: `spaCy` (`en_core_web_sm`) mixed with Regex targets industrial heuristics (e.g., Equipment IDs, Pressures, Dates, Engineers).
4. **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`) embed the chunks into 384-dimension float vectors.
5. **JSON Export & Vector Sandbox**: Generates the final output `output/json/*.json` contract. Also silently upserts to a local ChromaDB instance to allow semantic search sandboxing via `/search`.

## Installation & Setup

1. **Create Virtual Environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```
3. *(Optional)* **Run Uvicorn Server**:
   ```powershell
   python -m uvicorn app:app --host 127.0.0.1 --port 8000
   ```

*Note: On first execution, the pipeline will automatically download the `spaCy` NLP model and the `SentenceTransformer` neural network weights. PaddleOCR models will also be cached locally.*

---

## API Reference

### 1. Upload a Document
Upload a document. Supported formats: `.pdf`, `.docx`, `.xlsx`, `.png`, `.jpg`, `.jpeg`.

**Request:**
```bash
curl -X POST -F "file=@tests/sample_files/test.pdf" http://127.0.0.1:8000/upload
```
**Response:**
```json
{
  "document_id": "06ada9dc-a85b-497c-a757-67bad66b4ab5",
  "filename": "test.pdf",
  "status": "uploaded"
}
```

### 2. Trigger Processing Job
Asynchronously begin processing the document.

**Request:**
```bash
curl -X POST -H "Content-Type: application/json" -d '{"document_id": "06ada9dc-a85b-497c-a757-67bad66b4ab5"}' http://127.0.0.1:8000/process
```
**Response:**
```json
{
  "document_id": "06ada9dc-a85b-497c-a757-67bad66b4ab5",
  "status": "processing"
}
```

### 3. Check Job Status & Retrieve Export
Poll this endpoint. When `status` transitions to `completed`, the integration payload will be returned in the `result` field.

**Request:**
```bash
curl http://127.0.0.1:8000/document/06ada9dc-a85b-497c-a757-67bad66b4ab5
```
**Response (Simplified):**
```json
{
  "status": "completed",
  "error": null,
  "result": {
    "document_id": "06ada9dc-a85b-497c-a757-67bad66b4ab5",
    "filename": "test.pdf",
    "document_type": "pdf_document",
    "processed_at": "2026-07-19T17:11:15.710825",
    "page_count": 2,
    "entities": {
      "equipment": [],
      "fault": null,
      "manufacturer": "PDF Document"
    },
    "chunks": [
      {
        "chunk_id": "bd08fe10-7fa2-4c77-bf7b-60d2e172fb14",
        "page_number": 1,
        "text": "Test PDF Document Digital Page",
        "char_count": 30,
        "embedding": [0.0123, -0.045],
        "entities": {}
      }
    ]
  }
}
```

### 4. Semantic Search Sandbox
A convenience endpoint to verify embeddings against the local ChromaDB database.

**Request:**
```bash
curl "http://127.0.0.1:8000/search?q=Digital%20Page&top_k=1"
```

---

## Output JSON Schema (Knowledge Graph Handoff Contract)

The pipeline deposits finalized output structurally matching the API payload above directly into `output/json/`. 
- **Strict Pydantic Validation**: Missing values are rigorously guarded and emitted as explicit JSON `null` parameters to prevent `KeyError`s during downstream Neo4j ingest.
- **Embedded Arrays**: The raw 384-dimensional floating point vectors are stored identically in the `embedding` key for every chunk, allowing immediate Vector Index generation by the Knowledge Graph team.

## Directory Structure
```
d:\LAKSHYA\Desktop\AetherNexus\document_pipeline\
├── app.py                 # FastAPI routing and job status logic
├── pipeline.py            # Orchestrator for the background worker
├── config.py              # Central configurations and thresholds
├── chunking/              # Overlapping string windowing logic
├── embedding/             # SentenceTransformer singleton
├── entity/                # Regex & NLP based Named Entity Extraction
├── ocr/                   # PaddleOCR wrappers
├── parsers/               # File format ingestion modules
├── utils/                 # JSON schema generation and loggers
├── vector_db/             # Optional ChromaDB setup
├── uploads/               # Raw binaries
└── output/
    ├── json/              # Final exported contract files
    └── logs/              # Structured logging traces (pipeline.log)
```

## Known Limitations & Configuration Constraints

- **Corrupt PDFs**: Secure or damaged PDFs will raise a `ValueError` inside `parsers/pdf_parser.py`, which is elegantly trapped by the `pipeline.py` orchestrator and stored in the `/document/{id}` API JSON as `{"status": "failed", "error": "Unable to read PDF file..."}`.
- **OCR Fallback Threshold**: Set internally via `SCANNED_PDF_TEXT_THRESHOLD = 50`. If a PDF page produces fewer than 50 text characters using `PyMuPDF`, the page is classified as scanned and is forcefully routed to the OCR engine.
- **Missing ChromaDB**: If the local `vector_db` instantiation fails, the pipeline will merely log a warning and continue finalizing the critical JSON output. The sandbox is non-blocking.
