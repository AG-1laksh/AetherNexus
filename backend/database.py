import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    # verify connectivity on startup so we fail early if DB is offline
    driver.verify_connectivity()
except Exception as e:
    print(f"Warning: Could not connect to Neo4j database at {NEO4J_URI}.")
    print(f"Error: {e}")
    driver = None

def init_db():
    """Initialize database constraints and vector indexes."""
    if driver is None:
        print("Database not initialized, driver is None.")
        return
    with driver.session() as session:
        # Create constraint for unique Document filenames
        session.run("CREATE CONSTRAINT doc_filename IF NOT EXISTS FOR (d:Document) REQUIRE d.filename IS UNIQUE")
        # Create constraint for unique TextChunks
        session.run("CREATE CONSTRAINT chunk_id IF NOT EXISTS FOR (c:TextChunk) REQUIRE c.chunk_id IS UNIQUE")
        # Note: Vector index creation is specific to Neo4j version and embedding dimensions.
        # This is a placeholder for the actual vector index creation query.
        print("Database initialized.")

def close_db():
    if driver:
        driver.close()

def ingest_document_to_neo4j(doc_data: dict):
    """
    Ingests a document, its chunks, and entities into Neo4j.
    Expects TM1's JSON format.
    """
    # Flatten entities from dict to list of {label, name} for Cypher
    for chunk in doc_data.get('chunks', []):
        flat_entities = []
        entities_dict = chunk.get('entities', {})
        for key, value in entities_dict.items():
            if value is None:
                continue
            if isinstance(value, list):
                for item in value:
                    flat_entities.append({"label": key, "name": str(item)})
            else:
                flat_entities.append({"label": key, "name": str(value)})
        chunk['flat_entities'] = flat_entities

    query = """
    // 1. Create the Document Node
    MERGE (d:Document {document_id: $document_id})
    SET d.filename = $filename,
        d.doc_type = $document_type,
        d.timestamp = $processed_at

    // 2. Process each TextChunk
    WITH d
    UNWIND $chunks as chunk
    MERGE (c:TextChunk {chunk_id: chunk.chunk_id})
    SET c.text = chunk.text
    
    // In a real scenario, we would also set the vector embedding here using db.create.setNodeVectorProperty
    // e.g., CALL db.create.setNodeVectorProperty(c, 'embedding', chunk.embedding)

    // Link chunk to document
    MERGE (c)-[:PART_OF]->(d)

    // 3. Process Entities within the chunk
    WITH c, chunk
    UNWIND chunk.flat_entities as entity
    MERGE (e:Entity {name: entity.name})
    SET e.label = entity.label

    // Link entity to chunk
    MERGE (c)-[:MENTIONS]->(e)
    """
    
    if driver is None:
        print("Error: Neo4j driver is not initialized.")
        return 0

    with driver.session() as session:
        result = session.run(query, 
                             document_id=doc_data.get('document_id', ''),
                             filename=doc_data['filename'],
                             document_type=doc_data['document_type'],
                             processed_at=doc_data['processed_at'],
                             chunks=doc_data['chunks'])
        return result.consume().counters.nodes_created

def search_graph_by_embedding(embedding: list, top_k: int = 3):
    """
    Searches the graph for similar text chunks and traverses to get context.
    (Placeholder for actual vector search query)
    """
    query = """
    // NOTE: This requires a vector index named 'chunk_embeddings' to be created first.
    // CALL db.index.vector.queryNodes('chunk_embeddings', $top_k, $embedding)
    // YIELD node AS c, score
    
    // For now, we simulate finding a chunk and getting its document
    MATCH (c:TextChunk)-[:PART_OF]->(d:Document)
    OPTIONAL MATCH (c)-[:MENTIONS]->(e:Entity)
    RETURN c.text AS text, d.filename AS filename, d.source_url AS source_url, 0.95 AS score, collect(e.name) AS entities
    LIMIT $top_k
    """
    
    if driver is None:
        print("Error: Neo4j driver is not initialized.")
        return []

    # Simulating a response for the hackathon setup
    with driver.session() as session:
        result = session.run(query, top_k=top_k)
        return [record.data() for record in result]
