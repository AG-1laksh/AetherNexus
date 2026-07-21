import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import OUTPUT_JSON_DIR
from utils.logger import setup_logger

logger = setup_logger(__name__)

def get_status_file_path(document_id: str) -> Path:
    return OUTPUT_JSON_DIR / f"{document_id}.status.json"

def update_status(document_id: str, status: str, current_stage: Optional[str] = None, error: Optional[str] = None):
    """
    Atomically writes the job status to disk.
    status: 'processing', 'completed', 'failed'
    current_stage: e.g. 'parsing', 'chunking', 'embedding', etc.
    """
    status_path = get_status_file_path(document_id)
    
    data = {
        "status": status,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # Preserve existing current_stage if not explicitly overridden (useful when failing)
    if current_stage is not None:
        data["current_stage"] = current_stage
    elif status_path.exists():
        existing = get_status(document_id)
        if existing and "current_stage" in existing:
            data["current_stage"] = existing["current_stage"]

    if error is not None:
        data["error"] = error
        
    try:
        # Atomic write to prevent corruption if process is killed mid-write
        fd, temp_path = tempfile.mkstemp(dir=OUTPUT_JSON_DIR, prefix=f"{document_id}_", suffix=".tmp")
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        os.replace(temp_path, status_path)
    except Exception as e:
        logger.error(f"Failed to write status for {document_id}: {e}")

def get_status(document_id: str) -> Optional[dict]:
    """Reads status from disk, returns None if not found."""
    status_path = get_status_file_path(document_id)
    if not status_path.exists():
        return None
        
    try:
        with open(status_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to read status for {document_id}: {e}")
        return None
