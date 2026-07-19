"""
FastAPI application entry point for the Document Intelligence Pipeline.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Document Intelligence Pipeline",
    description="Industrial Knowledge Intelligence Platform — document ingestion, OCR, chunking, entity extraction, and vector storage.",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Liveness / readiness probe."""
    return {"status": "ok"}
