"""
Entity extractor — identifies domain-specific entities
(equipment IDs, standards, chemicals, etc.) from text.
"""


class EntityExtractor:
    """Extract named entities from industrial document text."""

    def __init__(self) -> None:
        """Initialize the NLP pipeline (lazy-loaded)."""
        self._nlp = None

    def extract(self, text: str) -> list[dict[str, str]]:
        """
        Extract entities from *text*.

        Args:
            text: Input text to process.

        Returns:
            List of dicts with keys 'text', 'label', 'start', 'end'.
        """
        raise NotImplementedError("EntityExtractor.extract() — implementation pending")
