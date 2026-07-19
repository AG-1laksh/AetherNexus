import logging
from typing import List
from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION

logger = logging.getLogger(__name__)

# Module-level singleton
_model = None

def get_embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info(f"Loading embedding model {EMBEDDING_MODEL_NAME}...")
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        
        # Verify dimension matches config
        model_dim = _model.get_embedding_dimension()
        if model_dim != EMBEDDING_DIMENSION:
            raise ValueError(
                f"Config dimension ({EMBEDDING_DIMENSION}) does not match "
                f"actual model dimension ({model_dim})."
            )
    return _model

def embed_text(text: str) -> List[float]:
    """Embed a single text string."""
    model = get_embedding_model()
    # model.encode returns a numpy array, convert to list of floats
    embedding = model.encode(text)
    return embedding.tolist()

def embed_batch(texts: List[str]) -> List[List[float]]:
    """Embed a batch of text strings efficiently."""
    if not texts:
        return []
    model = get_embedding_model()
    embeddings = model.encode(texts)
    return embeddings.tolist()
