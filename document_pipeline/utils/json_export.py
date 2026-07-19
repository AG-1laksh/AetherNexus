import os
import json
import logging
from typing import List
from pathlib import Path
from pydantic import BaseModel

from entity.extractor import ExtractedEntities
from config import OUTPUT_JSON_DIR

logger = logging.getLogger(__name__)

class ExportedChunk(BaseModel):
    chunk_id: str
    page_number: int
    text: str
    char_count: int
    embedding: List[float]
    entities: ExtractedEntities

class ExportedDocument(BaseModel):
    document_id: str
    filename: str
    document_type: str
    processed_at: str
    page_count: int
    entities: ExtractedEntities
    chunks: List[ExportedChunk]

def export_to_json(doc: ExportedDocument) -> Path:
    """
    Validates the ExportedDocument and writes it to disk as a JSON file.
    Ensures missing values are serialized as `null` rather than omitted.
    """
    try:
        # Pydantic inherently validates upon model instantiation,
        # but calling model_dump validates everything strictly during serialization.
        
        # We use exclude_none=False to ensure fields with None are serialized as null.
        # This guarantees a stable JSON contract for Teammate 2's ingestor.
        data_dict = doc.model_dump(mode="json", exclude_none=False)
        
        out_path = OUTPUT_JSON_DIR / f"{doc.document_id}.json"
        
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Successfully exported {doc.filename} to {out_path}")
        return out_path
        
    except Exception as e:
        logger.error(f"Failed to validate or export document JSON: {e}")
        raise
