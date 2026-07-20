import json
import os
import sys

# TM1's simulated JSON output
dummy_data = {
    "document_id": "test-doc-001",
    "filename": "pump_maintenance_report.pdf",
    "document_type": "maintenance_report",
    "processed_at": "2026-07-19T12:00:00Z",
    "page_count": 2,
    "entities": {
        "equipment": ["Pump P-101"],
        "fault": "Bearing Failure",
        "temperature": "90 C",
        "pressure": None,
        "date": "2025-03-01",
        "engineer": "J. Rao",
        "technician": None,
        "department": "Maintenance",
        "location": "Plant B",
        "manufacturer": "Acme Pumps",
        "serial_number": "SN-998877",
        "maintenance_action": "Bearing replaced"
    },
    "chunks": [
        {
            "chunk_id": "chunk-001",
            "page_number": 1,
            "text": "Maintenance was performed on Pump P-101. The ambient temperature was measured at 90 C. Failure Cause: Bearing Failure. Technician J. Rao conducted the work. Bearing replaced.",
            "char_count": 174,
            "embedding": [0.12, -0.05, 0.99, 0.42],  # truncated dummy embedding
            "entities": {
                "equipment": ["Pump P-101"],
                "fault": "Bearing Failure",
                "temperature": "90 C",
                "engineer": "J. Rao",
                "maintenance_action": "Bearing replaced"
            }
        }
    ]
}

if __name__ == "__main__":
    try:
        from database import ingest_document_to_neo4j
        print("Connecting to Neo4j and inserting document...")
        nodes_created = ingest_document_to_neo4j(dummy_data)
        print(f"SUCCESS! Created {nodes_created} nodes/relationships in Neo4j.")
    except Exception as e:
        print(f"Error during ingestion: {e}")
