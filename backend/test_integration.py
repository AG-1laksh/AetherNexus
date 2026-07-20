from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

print("--- Testing TM1 Ingestion (POST /api/ingest/document) ---")
dummy_data = {
    "document_id": "test-doc-002",
    "filename": "valve_inspection.pdf",
    "document_type": "inspection",
    "processed_at": "2026-07-20T12:00:00Z",
    "page_count": 1,
    "entities": {
        "equipment": ["Valve V-200"],
        "fault": "Leak",
        "temperature": "120 C"
    },
    "chunks": [
        {
            "chunk_id": "chunk-002",
            "page_number": 1,
            "text": "Valve V-200 was inspected. A minor leak was detected. Temperature 120 C.",
            "char_count": 72,
            "embedding": [0.1, 0.2, 0.3],
            "entities": {
                "equipment": ["Valve V-200"],
                "fault": "Leak",
                "temperature": "120 C"
            }
        }
    ]
}

# The TestClient automatically runs the lifespan events (which connects/disconnects DB)
with client:
    response = client.post("/api/ingest/document", json=dummy_data)
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

    print("\n--- Testing TM3 Query (POST /api/query/) ---")
    query_data = {
        "question": "What is the status of Valve V-200?",
        "top_k": 3
    }
    response_q = client.post("/api/query/", json=query_data)
    print("Status Code:", response_q.status_code)
    print("Response JSON:", json.dumps(response_q.json(), indent=2))
