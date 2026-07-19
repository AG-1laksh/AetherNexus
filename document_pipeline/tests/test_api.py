import asyncio
import httpx
import time
import json
from pathlib import Path

# We assume the FastAPI server is running on http://127.0.0.1:8000
BASE_URL = "http://127.0.0.1:8000"
TEST_PDF_PATH = Path(__file__).resolve().parent / "sample_files" / "test.pdf"

async def test_api():
    print("=== Testing FastAPI Integration ===\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Health check
        print("1. Checking Health...")
        health_resp = await client.get(f"{BASE_URL}/health")
        print(f"Health: {health_resp.json()}\n")
        
        # 2. Upload file
        if not TEST_PDF_PATH.exists():
            print(f"Test PDF not found at {TEST_PDF_PATH}. Creating a dummy text file to test upload rejection.")
            return
            
        print("2. Uploading File...")
        with open(TEST_PDF_PATH, "rb") as f:
            files = {"file": (TEST_PDF_PATH.name, f, "application/pdf")}
            upload_resp = await client.post(f"{BASE_URL}/upload", files=files)
            
        upload_data = upload_resp.json()
        print(f"Upload Response: {upload_data}")
        document_id = upload_data["document_id"]
        print(f"Document ID: {document_id}\n")
        
        # 3. Process Document
        print("3. Triggering Processing...")
        process_resp = await client.post(f"{BASE_URL}/process", json={"document_id": document_id})
        print(f"Process Response: {process_resp.json()}\n")
        
        # 4. Polling for Completion
        print("4. Polling for Completion...")
        status = "processing"
        attempts = 0
        while status == "processing" and attempts < 45:
            await asyncio.sleep(3)
            doc_resp = await client.get(f"{BASE_URL}/document/{document_id}")
            doc_data = doc_resp.json()
            status = doc_data.get("status")
            print(f"  Attempt {attempts+1} | Status: {status}")
            attempts += 1
            
        if status == "completed":
            print("\nProcessing Completed! Final JSON Result:")
            result = doc_data.get("result")
            # Truncate embedding for display
            if result and "chunks" in result:
                for c in result["chunks"]:
                    if "embedding" in c and len(c["embedding"]) > 3:
                        c["embedding"] = c["embedding"][:3] + ["... (truncated for display)"]
            
            print(json.dumps(result, indent=2))
        else:
            print(f"\nProcessing did not complete normally. Status: {status}")
            
        # 5. Test Search Endpoint
        print("\n5. Testing Semantic Search Endpoint...")
        search_query = "What is this document about?"
        search_resp = await client.get(f"{BASE_URL}/search", params={"q": search_query, "top_k": 2})
        if search_resp.status_code == 200:
             print("Search successful:")
             print(json.dumps(search_resp.json(), indent=2))
        else:
             print(f"Search failed: {search_resp.status_code} {search_resp.text}")

if __name__ == "__main__":
    asyncio.run(test_api())
