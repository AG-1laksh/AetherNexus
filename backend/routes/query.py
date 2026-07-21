from fastapi import APIRouter, HTTPException
from models import QueryRequest, QueryResponse, SourceCitation
import database

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def query_graph(request: QueryRequest):
    """
    Endpoint for Team Member 3 (Frontend/AI Copilot) to ask questions.
    Performs Graph RAG by searching vector embeddings and traversing the graph.
    """
    try:
        # In a real implementation, you would convert request.question into a vector embedding here
        # using the same model Team Member 1 used (e.g., OpenAI, HuggingFace).
        # dummy_embedding = get_embedding(request.question)
        dummy_embedding = [0.0] * 1536 # Placeholder
        
        # Search Neo4j
        results = database.search_graph_by_embedding(dummy_embedding, top_k=request.top_k)
        
        # Format the response for the frontend
        citations = []
        all_entities = set()
        
        for record in results:
            citations.append(SourceCitation(
                filename=record.get("filename", "Unknown"),
                source_url=record.get("source_url", ""),
                text_snippet=record.get("text", ""),
                confidence_score=record.get("score", 0.0)
            ))
            
            # Collect unique entities found in the graph traversal
            entities_in_record = record.get("entities", [])
            for e in entities_in_record:
                all_entities.add(e)
                
        return QueryResponse(
            context_chunks=citations,
            graph_entities=[{"name": e} for e in all_entities],
            message="Successfully retrieved context from Knowledge Graph."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
