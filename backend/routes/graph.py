from fastapi import APIRouter, HTTPException
from models import GraphResponse
import database

router = APIRouter()

@router.get("/", response_model=GraphResponse)
async def get_graph(limit: int = 50):
    """
    Returns Document/TextChunk/Entity nodes and relationships for the
    Knowledge Graph visualization (React Flow).
    """
    try:
        graph = database.get_knowledge_graph(limit=limit)
        return GraphResponse(**graph)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
