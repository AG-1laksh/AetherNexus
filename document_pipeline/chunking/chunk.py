import uuid
import re
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# Chunk size constraints (in CHARACTERS, not tokens)
MIN_CHUNK_SIZE = 500
MAX_CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

class DocumentChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    page_number: int
    document_type: str
    text: str
    char_count: int

def chunk_document(pages: List[Dict[str, Any]], filename: str, document_type: str) -> List[DocumentChunk]:
    """
    Chunks a document page-by-page. Output chunks have 500-800 characters,
    with a 100 character overlap. Boundaries prefer paragraphs and sentences.
    """
    chunks = []
    
    for page in pages:
        page_number = page.get("page_number", 1)
        text = page.get("text", "")
        if not text.strip():
            continue
            
        # 1. Split into natural segments (sentences/paragraphs)
        paragraphs = re.split(r'\n\n+', text)
        segments = []
        for p in paragraphs:
            if len(p) <= MAX_CHUNK_SIZE:
                segments.append(p)
            else:
                # Split by sentences if the paragraph is too long
                sentences = re.split(r'(?<=[.!?])\s+', p)
                for s in sentences:
                    if s.strip():
                        segments.append(s)
                        
        # 2. Build overlapping chunks
        current_chunk = ""
        
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
                
            space = " " if current_chunk else ""
            
            # Case A: The segment itself is massively long (>800 chars)
            if len(segment) > MAX_CHUNK_SIZE:
                if current_chunk:
                    # Finalize pending buffer
                    chunks.append(DocumentChunk(
                        filename=filename, page_number=page_number, document_type=document_type,
                        text=current_chunk.strip(), char_count=len(current_chunk.strip())
                    ))
                    
                    # Generate overlap
                    overlap_text = current_chunk[-CHUNK_OVERLAP:] if len(current_chunk) >= CHUNK_OVERLAP else current_chunk
                    space_idx = overlap_text.find(' ')
                    if space_idx != -1 and space_idx < len(overlap_text) // 2:
                        overlap_text = overlap_text[space_idx+1:]
                    current_chunk = overlap_text + " "
                    
                # Hard slice the segment
                segment_to_slice = current_chunk + segment if current_chunk else segment
                i = 0
                while i < len(segment_to_slice):
                    end = min(i + MAX_CHUNK_SIZE, len(segment_to_slice))
                    slice_text = segment_to_slice[i:end]
                    
                    if end == len(segment_to_slice) and len(slice_text) < MIN_CHUNK_SIZE:
                        # Remainder is small, keep it as current_chunk for the next loop
                        current_chunk = slice_text
                        break
                        
                    chunks.append(DocumentChunk(
                        filename=filename, page_number=page_number, document_type=document_type,
                        text=slice_text.strip(), char_count=len(slice_text.strip())
                    ))
                    i += (MAX_CHUNK_SIZE - CHUNK_OVERLAP)
                    if i >= len(segment_to_slice):
                         current_chunk = ""
                         
            # Case B: Adding this segment exceeds MAX_CHUNK_SIZE
            elif len(current_chunk) + len(space) + len(segment) > MAX_CHUNK_SIZE:
                chunks.append(DocumentChunk(
                    filename=filename, page_number=page_number, document_type=document_type,
                    text=current_chunk.strip(), char_count=len(current_chunk.strip())
                ))
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-CHUNK_OVERLAP:] if len(current_chunk) >= CHUNK_OVERLAP else current_chunk
                space_idx = overlap_text.find(' ')
                if space_idx != -1 and space_idx < len(overlap_text) // 2:
                    overlap_text = overlap_text[space_idx+1:]
                
                current_chunk = overlap_text + " " + segment
                
            # Case C: Segment fits into current chunk
            else:
                current_chunk = current_chunk + space + segment if current_chunk else segment
                
        # Add remainder for this page
        if current_chunk.strip():
             chunks.append(DocumentChunk(
                 filename=filename, page_number=page_number, document_type=document_type,
                 text=current_chunk.strip(), char_count=len(current_chunk.strip())
             ))
             
    return chunks
