from fastapi import APIRouter, HTTPException
from models import DocumentIngestRequest, IngestResponse
import database

router = APIRouter()

@router.post("/document", response_model=IngestResponse)
async def ingest_document(request: DocumentIngestRequest):
    """
    Endpoint for Team Member 1 to send processed documents.
    Takes the JSON payload, extracts chunks and entities, and stores them in Neo4j.
    """
    try:
        # Convert Pydantic model to dict for the database function
        doc_data = request.model_dump()
        
        # Call the database function to insert into Neo4j
        nodes_created = database.ingest_document_to_neo4j(doc_data)
        
        return IngestResponse(
            status="success",
            message=f"Document {request.filename} ingested successfully.",
            nodes_created=nodes_created
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
