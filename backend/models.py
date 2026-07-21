from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- INGESTION MODELS (Team Member 1 -> Backend) ---

class ExtractedEntities(BaseModel):
    equipment: List[str] = []
    fault: Optional[str] = None
    temperature: Optional[str] = None
    pressure: Optional[str] = None
    date: Optional[str] = None
    engineer: Optional[str] = None
    technician: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    manufacturer: Optional[str] = None
    serial_number: Optional[str] = None
    maintenance_action: Optional[str] = None

class ExportedChunk(BaseModel):
    chunk_id: str
    page_number: int
    text: str
    char_count: int
    embedding: List[float]
    entities: ExtractedEntities

class DocumentIngestRequest(BaseModel):
    document_id: str
    filename: str
    document_type: str
    processed_at: str
    page_count: int
    entities: ExtractedEntities
    chunks: List[ExportedChunk]

class IngestResponse(BaseModel):
    status: str
    message: str
    nodes_created: int

# --- QUERY MODELS (Frontend -> Backend) ---

class QueryRequest(BaseModel):
    question: str = Field(..., description="User's query")
    top_k: int = Field(default=3, description="Number of results to return")

class SourceCitation(BaseModel):
    filename: str
    source_url: Optional[str] = None
    text_snippet: str
    confidence_score: float

class QueryResponse(BaseModel):
    context_chunks: List[SourceCitation]
    graph_entities: List[Dict[str, Any]] = Field(description="Related entities pulled from the Knowledge Graph")
    message: str = "Query processed successfully"

# --- DASHBOARD MODELS (Backend -> Frontend) ---

class DashboardTotals(BaseModel):
    documents: int
    equipment: int
    maintenance_reports: int

class MostFailedEquipment(BaseModel):
    id: str
    name: str
    failures: int

class DashboardResponse(BaseModel):
    totals: DashboardTotals
    most_failed_equipment: Optional[MostFailedEquipment] = None
    charts: Dict[str, Any] = Field(default_factory=dict)

# --- EQUIPMENT MODELS (Backend -> Frontend) ---

class EquipmentResponse(BaseModel):
    id: str
    name: str
    location: Optional[str] = None
    maintenance_count: int
    failure_count: int
    last_inspection: Optional[str] = None
    last_maintenance: Optional[str] = None
    status: str = "unknown"

# --- KNOWLEDGE GRAPH MODELS (Backend -> Frontend) ---

class GraphNode(BaseModel):
    id: str
    data: Dict[str, Any]
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
