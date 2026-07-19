"""
Centralized configuration for the Document Intelligence Pipeline.

All paths, constants, and environment-loaded settings live here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env file (if present) into os.environ
# ---------------------------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------------------------
# Base directory (this file's parent)
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# File-system paths
# ---------------------------------------------------------------------------
UPLOAD_DIR: Path = BASE_DIR / "uploads"
OUTPUT_JSON_DIR: Path = BASE_DIR / "output" / "json"
OUTPUT_CHUNKS_DIR: Path = BASE_DIR / "output" / "chunks"

# Ensure directories exist at import time
for _dir in (UPLOAD_DIR, OUTPUT_JSON_DIR, OUTPUT_CHUNKS_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Chunking constants
# ---------------------------------------------------------------------------
CHUNK_SIZE: int = 512          # max tokens per chunk
CHUNK_OVERLAP: int = 64        # overlap tokens between consecutive chunks

# ---------------------------------------------------------------------------
# Scanned-PDF detection threshold
# ---------------------------------------------------------------------------
# If a PDF page yields fewer than this many characters of extractable text,
# it is treated as a scanned/image page and routed through OCR.
SCANNED_PDF_TEXT_THRESHOLD: int = 50

# ---------------------------------------------------------------------------
# OCR settings
# ---------------------------------------------------------------------------
OCR_CONFIDENCE_THRESHOLD: float = 0.6

# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION: int = 384

# ---------------------------------------------------------------------------
# Neo4j AuraDB connection (loaded from environment variables)
# ---------------------------------------------------------------------------
NEO4J_URI: str = os.getenv("NEO4J_URI", "neo4j+s://localhost:7687")
NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")
NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")
VECTOR_INDEX_NAME: str = "document_embeddings"
