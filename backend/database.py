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

def get_dashboard_stats():
    """
    Aggregates counts and failure/maintenance breakdowns from the graph
    for the Dashboard page.
    """
    if driver is None:
        print("Error: Neo4j driver is not initialized.")
        return None

    with driver.session() as session:
        totals = session.run(
            """
            OPTIONAL MATCH (d:Document)
            WITH count(DISTINCT d) AS documents
            OPTIONAL MATCH (e:Entity {label: 'equipment'})
            WITH documents, count(DISTINCT e) AS equipment
            OPTIONAL MATCH (c:TextChunk)-[:MENTIONS]->(:Entity {label: 'fault'})
            RETURN documents, equipment, count(DISTINCT c) AS maintenance_reports
            """
        ).single()

        failures = session.run(
            """
            MATCH (eq:Entity {label: 'equipment'})<-[:MENTIONS]-(c:TextChunk)-[:MENTIONS]->(:Entity {label: 'fault'})
            RETURN eq.name AS name, count(DISTINCT c) AS failures
            ORDER BY failures DESC
            LIMIT 5
            """
        )
        equipment_failures = [record.data() for record in failures]

        uploads = session.run(
            """
            MATCH (d:Document)
            RETURN substring(d.timestamp, 0, 7) AS month, count(d) AS count
            ORDER BY month
            """
        )
        documents_uploaded = [record.data() for record in uploads if record["month"]]

        return {
            "totals": {
                "documents": totals["documents"] or 0,
                "equipment": totals["equipment"] or 0,
                "maintenance_reports": totals["maintenance_reports"] or 0,
            },
            "equipment_failures": equipment_failures,
            "documents_uploaded": documents_uploaded,
        }


def get_equipment_by_id(equipment_id: str):
    """
    Looks up a single equipment Entity node (case-insensitive name match)
    and derives maintenance/failure counts and dates from linked chunks.
    """
    if driver is None:
        print("Error: Neo4j driver is not initialized.")
        return None

    with driver.session() as session:
        record = session.run(
            """
            MATCH (eq:Entity {label: 'equipment'})
            WHERE toLower(eq.name) CONTAINS toLower($equipment_id)
            OPTIONAL MATCH (eq)<-[:MENTIONS]-(c:TextChunk)-[:PART_OF]->(d:Document)
            OPTIONAL MATCH (c)-[:MENTIONS]->(fault:Entity {label: 'fault'})
            OPTIONAL MATCH (c)-[:MENTIONS]->(loc:Entity {label: 'location'})
            RETURN eq.name AS name,
                   collect(DISTINCT loc.name)[0] AS location,
                   count(DISTINCT c) AS maintenance_count,
                   count(DISTINCT fault) AS failure_count,
                   max(d.timestamp) AS last_maintenance
            """,
            equipment_id=equipment_id,
        ).single()

        if record is None or record["name"] is None:
            return None

        return record.data()


def get_knowledge_graph(limit: int = 50):
    """
    Returns a bounded set of Document/TextChunk/Entity nodes and their
    relationships for the React Flow visualization.
    """
    if driver is None:
        print("Error: Neo4j driver is not initialized.")
        return {"nodes": [], "edges": []}

    with driver.session() as session:
        result = session.run(
            """
            MATCH (d:Document)<-[:PART_OF]-(c:TextChunk)-[:MENTIONS]->(e:Entity)
            RETURN d, c, e
            LIMIT $limit
            """,
            limit=limit,
        )

        nodes = {}
        edges = []

        for record in result:
            d, c, e = record["d"], record["c"], record["e"]

            doc_id = f"document-{d['document_id']}"
            chunk_id = f"chunk-{c['chunk_id']}"
            entity_id = f"entity-{e['name']}"

            nodes.setdefault(doc_id, {"id": doc_id, "data": {"label": d["filename"], "type": "document"}})
            nodes.setdefault(chunk_id, {"id": chunk_id, "data": {"label": c["chunk_id"], "type": "chunk"}})
            nodes.setdefault(entity_id, {"id": entity_id, "data": {"label": e["name"], "type": "equipment" if e.get("label") == "equipment" else "entity"}})

            edges.append({"id": f"{chunk_id}-part_of-{doc_id}", "source": chunk_id, "target": doc_id, "label": "part_of"})
            edges.append({"id": f"{chunk_id}-mentions-{entity_id}", "source": chunk_id, "target": entity_id, "label": "mentions"})

        return {"nodes": list(nodes.values()), "edges": edges}


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
