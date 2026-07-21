from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database
from routes import ingest, query, dashboard, equipment, graph

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield
    database.close_db()

app = FastAPI(
    title="Aether-Nexus Industrial Knowledge API",
    description="Backend API for document ingestion and graph-based querying.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For hackathon, allow all. In prod, restrict this.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Include routers
app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(query.router, prefix="/api/query", tags=["Query"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(equipment.router, prefix="/api/equipment", tags=["Equipment"])
app.include_router(graph.router, prefix="/api/graph", tags=["Knowledge Graph"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Aether-Nexus API. Visit /docs for Swagger UI."}
