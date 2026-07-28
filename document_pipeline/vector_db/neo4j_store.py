"""
Neo4j AuraDB vector store — stores document chunks and their
embeddings in a Neo4j graph database with vector index support.
"""

import logging
from typing import List, Dict, Any, Optional

from neo4j import GraphDatabase

from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

logger = logging.getLogger(__name__)


class Neo4jVectorStore:
    """Manage document chunk storage in Neo4j AuraDB."""

    def __init__(self) -> None:
        self._driver = None
        try:
            self._driver = GraphDatabase.driver(
                NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
            )
            self._driver.verify_connectivity()
            logger.info("Connected to Neo4j AuraDB successfully.")
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j: {e}")
            self._driver = None

    @property
    def is_connected(self) -> bool:
        return self._driver is not None

    def _ensure_constraints(self) -> None:
        """Create uniqueness constraints if they don't already exist."""
        if not self.is_connected:
            return
        with self._driver.session(database=NEO4J_DATABASE) as session:
            session.run(
                "CREATE CONSTRAINT doc_filename IF NOT EXISTS "
                "FOR (d:Document) REQUIRE d.filename IS UNIQUE"
            )
            session.run(
                "CREATE CONSTRAINT chunk_id IF NOT EXISTS "
                "FOR (c:TextChunk) REQUIRE c.chunk_id IS UNIQUE"
            )

    def store_document(self, doc_data: Dict[str, Any]) -> int:
        """
        Store a full document (with chunks and entities) into Neo4j.
        Uses the same Cypher pattern as backend/database.py so both
        services produce an identical graph schema.

        Args:
            doc_data: Dictionary matching ExportedDocument schema.

        Returns:
            Number of nodes created.
        """
        if not self.is_connected:
            logger.warning("Neo4j not connected — skipping store.")
            return 0

        # Flatten entities for each chunk so Cypher can UNWIND them
        for chunk in doc_data.get("chunks", []):
            flat_entities: List[Dict[str, str]] = []
            entities_dict = chunk.get("entities", {})
            for key, value in entities_dict.items():
                if value is None:
                    continue
                if isinstance(value, list):
                    for item in value:
                        flat_entities.append({"label": key, "name": str(item)})
                else:
                    flat_entities.append({"label": key, "name": str(value)})
            chunk["flat_entities"] = flat_entities

        query = """
        // 1. Create or update the Document node by unique filename
        MERGE (d:Document {filename: $filename})
        SET d.document_id = $document_id,
            d.doc_type    = $document_type,
            d.timestamp   = $processed_at,
            d.page_count  = $page_count

        // 2. Create TextChunk nodes and link to Document
        WITH d
        UNWIND $chunks AS chunk
        MERGE (c:TextChunk {chunk_id: chunk.chunk_id})
        SET c.text       = chunk.text,
            c.page_number = chunk.page_number,
            c.char_count  = chunk.char_count
        MERGE (c)-[:PART_OF]->(d)

        // 3. Create Entity nodes and link to TextChunk
        WITH c, chunk
        UNWIND chunk.flat_entities AS entity
        MERGE (e:Entity {name: entity.name})
        SET e.label = entity.label
        MERGE (c)-[:MENTIONS]->(e)
        """

        try:
            self._ensure_constraints()
            with self._driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(
                    query,
                    document_id=doc_data.get("document_id", ""),
                    filename=doc_data.get("filename", ""),
                    document_type=doc_data.get("document_type", ""),
                    processed_at=doc_data.get("processed_at", ""),
                    page_count=doc_data.get("page_count", 0),
                    chunks=doc_data.get("chunks", []),
                )
                nodes_created = result.consume().counters.nodes_created
                logger.info(
                    f"Stored document {doc_data.get('document_id')} in Neo4j "
                    f"({nodes_created} nodes created)"
                )
                return nodes_created
        except Exception as e:
            logger.error(f"Failed to store document in Neo4j: {e}")
            return 0

    def close(self) -> None:
        """Close the database connection."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed.")
