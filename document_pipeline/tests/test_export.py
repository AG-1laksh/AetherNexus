import os
import sys
import uuid
import json
from datetime import datetime
from pathlib import Path

# Add parent dir to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from chunking.chunk import chunk_document
from entity.extractor import extract_entities, merge_entities
from embedding.embed import embed_text
from utils.json_export import ExportedDocument, ExportedChunk, export_to_json
from vector_db.chroma_store import LocalChromaStore

def main():
    print("=== Testing Full Pipeline to JSON Export ===\n")
    
    # Dummy Document
    document_id = str(uuid.uuid4())
    filename = "test_maintenance_report.pdf"
    
    dummy_text = (
        "Inspection Date: 2025-03-01. "
        "Maintenance was performed on Pump P-101. "
        "The ambient temperature was measured at 90 C. "
        "Failure Cause: Bearing Failure. "
        "Maintenance Action: Bearing replaced. "
        "Technician J. Rao conducted the work."
    )
    
    pages = [
        {
            "page_number": 2,
            "text": dummy_text,
            "source": "digital"
        }
    ]
    
    # 1. Chunking
    chunks = chunk_document(pages, filename=filename, document_type="maintenance_report")
    print(f"Generated {len(chunks)} chunks.")
    
    # 2. Entity Extraction & 3. Embeddings
    exported_chunks = []
    chunk_entities_list = []
    
    for c in chunks:
        # Extract
        ents = extract_entities(c.text)
        chunk_entities_list.append(ents)
        
        # Embed
        embedding = embed_text(c.text)
        
        # Create ExportedChunk
        exported_chunks.append(
            ExportedChunk(
                chunk_id=c.chunk_id,
                page_number=c.page_number,
                text=c.text,
                char_count=c.char_count,
                embedding=embedding,
                entities=ents
            )
        )
        
    # Document Level Entities
    doc_entities = merge_entities(chunk_entities_list)
    
    # 4. JSON Export Construction
    export_doc = ExportedDocument(
        document_id=document_id,
        filename=filename,
        document_type="maintenance_report",
        processed_at=datetime.now(datetime.UTC).isoformat(),
        page_count=5, # static dummy for test
        entities=doc_entities,
        chunks=exported_chunks
    )
    
    # Export to disk
    out_path = export_to_json(export_doc)
    print(f"\nSaved JSON to: {out_path}\n")
    
    # Print the JSON to terminal (truncated embedding for readability)
    with open(out_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # Truncate embedding array in display to avoid wall of text
        for c in data["chunks"]:
            if "embedding" in c and len(c["embedding"]) > 3:
                c["embedding"] = c["embedding"][:3] + ["... (truncated for display)"]
        print(json.dumps(data, indent=2))
        
    # 5. ChromaDB Sanity Test
    print("\n=== Testing ChromaDB Sanity Check ===")
    store = LocalChromaStore()
    if store.collection:
        ids = [c.chunk_id for c in exported_chunks]
        embeddings = [c.embedding for c in exported_chunks]
        texts = [c.text for c in exported_chunks]
        metadatas = [{"filename": filename}] * len(exported_chunks)
        
        print("Upserting to ChromaDB...")
        store.upsert_chunks(ids, embeddings, texts, metadatas)
        
        query_text = "Who replaced the bearing?"
        print(f"Querying ChromaDB for: '{query_text}'")
        query_embed = embed_text(query_text)
        
        res = store.query_similar(query_embed, top_k=1)
        if res and res.get("documents") and res["documents"][0]:
            print(f"Top Result: {res['documents'][0][0]}")
        else:
            print("No results found.")
            
if __name__ == "__main__":
    main()
