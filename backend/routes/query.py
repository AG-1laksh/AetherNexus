from fastapi import APIRouter, HTTPException
from models import QueryRequest, QueryResponse, SourceCitation
import database
import os
import httpx
from dotenv import load_dotenv

router = APIRouter()

from pathlib import Path

async def generate_gemini_answer(question: str, citations: list[SourceCitation], entities: set[str]) -> str | None:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "⚠️ *Gemini API Key not found in environment.* Here are the direct context extracts retrieved from your Knowledge Graph below:"
    
    # Construct context representation
    context_text = "\n\n".join([f"Document: {c.filename}\nSnippet: {c.text_snippet}" for c in citations])
    entities_text = ", ".join(list(entities)) if entities else "None identified"
    
    prompt = f"""You are Aether-Nexus, an advanced Industrial Knowledge Intelligence assistant.
Your task is to provide an accurate, clear, and insightful answer to the user's technical query using ONLY the document snippets and graph entities retrieved from our Neo4j Knowledge Graph below.

[User Query]
{question}

[Retrieved Knowledge Graph Context]
Entities Mentioned: {entities_text}
Document Snippets:
{context_text}

Instructions:
- Be helpful, professional, and well-structured. Use standard Markdown formatting (bullet points, bold text where helpful).
- Cite the relevant Document filename when referencing details from a snippet.
- If the answer is not contained in the provided context, clearly state that the information isn't in the uploaded knowledge graph."""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1024}
    }
    
    # We iterate over current supported model names starting with high-quota lite models to prevent 404 or 429 rate limit errors
    models_to_try = ["gemini-2.0-flash-lite-001", "gemini-2.0-flash-lite", "gemini-flash-lite-latest", "gemini-2.0-flash", "gemini-flash-latest", "gemini-pro-latest"]
    
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            for model_name in models_to_try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"]
                else:
                    print(f"Gemini model {model_name} returned status {resp.status_code}: {resp.text}")
                    continue
            return f"⚠️ *Gemini API temporarily rate-limited across all models.* Showing retrieved knowledge graph context below:"
    except Exception as e:
        print(f"Failed to call Gemini API: {e}")
        return "⚠️ *Could not connect to Gemini API.* Showing retrieved knowledge graph context below:"

@router.post("/", response_model=QueryResponse)
async def query_graph(request: QueryRequest):
    """
    Endpoint for Team Member 3 (Frontend/AI Copilot) to ask questions.
    Performs Graph RAG by searching vector embeddings and traversing the graph, then calling Gemini API.
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
                
        # Synthesize conversational answer using Gemini API
        answer = await generate_gemini_answer(request.question, citations, all_entities)
                
        return QueryResponse(
            answer=answer,
            context_chunks=citations,
            graph_entities=[{"name": e} for e in all_entities],
            message="Successfully retrieved context from Knowledge Graph."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
