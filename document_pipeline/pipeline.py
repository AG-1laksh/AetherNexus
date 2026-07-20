import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from config import OUTPUT_JSON_DIR
from parsers.pdf_parser import parse_pdf
from parsers.docx_parser import parse_docx
from parsers.excel_parser import parse_excel
from parsers.image_parser import parse_image
from utils.helpers import clean_text, get_file_extension
from chunking.chunk import chunk_document
from entity.extractor import extract_entities, merge_entities
from embedding.embed import embed_text
from utils.json_export import ExportedDocument, ExportedChunk, export_to_json
from vector_db.chroma_store import LocalChromaStore

from utils.logger import setup_logger

logger = setup_logger(__name__)

# Global in-memory job tracker for the MVP
JOB_STATUS: Dict[str, Dict[str, Any]] = {}

def get_document_type(ext: str) -> str:
    """Map file extensions to document_type labels."""
    if ext in ('png', 'jpg', 'jpeg'):
        return 'image_scan'
    elif ext == 'pdf':
        return 'pdf_document'
    elif ext == 'docx':
        return 'word_document'
    elif ext in ('xlsx', 'xls'):
        return 'excel_spreadsheet'
    return 'unknown_document'

def run_pipeline_task_subprocess(document_id: str, filepath: str, filename: str):
    """
    Background process task to process a document end-to-end.
    Runs inside a ProcessPoolExecutor to avoid event loop deadlocks.
    """
    logger.info(f"Started pipeline for {document_id} ({filename})")
    
    try:
        ext = get_file_extension(filename)
        document_type = get_document_type(ext)
        
        # 1. Parse
        if ext == 'pdf':
            pages = parse_pdf(filepath)
        elif ext == 'docx':
            pages = parse_docx(filepath)
        elif ext in ('xlsx', 'xls'):
            pages = parse_excel(filepath)
        elif ext in ('png', 'jpg', 'jpeg'):
            pages = parse_image(filepath)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")
            
        # Clean text in pages
        for page in pages:
            if "text" in page:
                page["text"] = clean_text(page["text"])
                
        # 2. Chunking
        chunks = chunk_document(pages, filename=filename, document_type=document_type)
        logger.info(f"Generated {len(chunks)} chunks for {document_id}")
        
        if not chunks:
             logger.warning(f"No text extracted for {document_id}")
             # We can still output an empty document
             
        # 3. Entities & 4. Embeddings
        exported_chunks = []
        chunk_entities_list = []
        
        for c in chunks:
            ents = extract_entities(c.text)
            chunk_entities_list.append(ents)
            
            emb = embed_text(c.text)
            
            exported_chunks.append(ExportedChunk(
                chunk_id=c.chunk_id,
                page_number=c.page_number,
                text=c.text,
                char_count=c.char_count,
                embedding=emb,
                entities=ents
            ))
            
        logger.info(f"Extracted entities and generated {len(exported_chunks)} embeddings for {document_id}")
            
        # Document Level Merging
        doc_entities = merge_entities(chunk_entities_list)
        
        # 5. JSON Export
        export_doc = ExportedDocument(
            document_id=document_id,
            filename=filename,
            document_type=document_type,
            processed_at=datetime.utcnow().isoformat(),
            page_count=len(pages),
            entities=doc_entities,
            chunks=exported_chunks
        )
        
        export_to_json(export_doc)
        
        # 6. Local Vector Upsert (Optional Sanity DB)
        try:
            store = LocalChromaStore()
            if store.collection and exported_chunks:
                ids = [c.chunk_id for c in exported_chunks]
                embeddings = [c.embedding for c in exported_chunks]
                texts = [c.text for c in exported_chunks]
                metadatas = [{"filename": filename, "document_id": document_id, "page_number": c.page_number} for c in exported_chunks]
                store.upsert_chunks(ids, embeddings, texts, metadatas)
                logger.info(f"Upserted {len(exported_chunks)} chunks to ChromaDB for {document_id}")
        except Exception as e:
            logger.warning(f"Failed to upsert to ChromaDB, but JSON export succeeded: {e}")
            
        # Done!
        logger.info(f"Completed pipeline for {document_id}")
        return True
        
    except Exception as e:
        logger.error(f"Pipeline failed for {document_id}: {e}")
        logger.error(traceback.format_exc())
        raise e
