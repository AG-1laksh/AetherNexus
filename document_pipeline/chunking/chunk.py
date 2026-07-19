"""
Text chunker — splits extracted document text into overlapping chunks
suitable for embedding and vector search.
"""


class TextChunker:
    """Split text into fixed-size overlapping chunks."""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 64) -> None:
        """
        Args:
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of overlapping characters between chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str) -> list[str]:
        """
        Split *text* into overlapping chunks.

        Args:
            text: The full document text.

        Returns:
            List of text chunks.
        """
        raise NotImplementedError("TextChunker.chunk() — implementation pending")
