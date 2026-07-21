import json
import urllib.request
import urllib.error

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
                "maintenance_action": "Bearing replaced",
                # Include other required fields as None to match Pydantic schema if not strict, 
                # but Pydantic BaseModel handles missing optional fields fine.
            }
        }
    ]
}

url = "http://127.0.0.1:8000/api/ingest/document"
data = json.dumps(dummy_data).encode("utf-8")
headers = {"Content-Type": "application/json"}

req = urllib.request.Request(url, data=data, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode())
        print("SUCCESS!")
        print(f"Status Code: {response.getcode()}")
        print(f"Response: {json.dumps(result, indent=2)}")
except urllib.error.HTTPError as e:
    print(f"FAILED!")
    print(f"Status Code: {e.code}")
    print(f"Response: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
