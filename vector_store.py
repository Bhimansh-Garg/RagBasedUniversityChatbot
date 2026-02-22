import numpy as np
import os
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

# ============ GLOBAL STATE ============

_documents = None
_embeddings = None
_model = None

def initialize_vector_store(documents: List[dict], rebuild: bool = False):
    """
    Initialize the vector store with documents
    
    Args:
        documents: List of dicts with 'text', 'source', 'page' keys
        rebuild: Force rebuild embeddings (ignore cache)
    
    This should be called ONCE in app.py startup
    """
    global _documents, _embeddings, _model
    
    _documents = documents
    
    # Load embedding model (downloads on first use, ~22MB)
    if _model is None:
        print("Loading embedding model (may take a minute on first run)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✓ Model loaded")
    
    print(f"Generating embeddings for {len(documents)} documents...")
    texts = [doc['text'] for doc in documents]
    
    # Generate embeddings
    _embeddings = _model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    _embeddings = np.array(_embeddings).astype("float32")
    
    print(f"✓ Embeddings generated. Shape: {_embeddings.shape}")


def search(query: str, top_k: int = 3, threshold: float = 0.25) -> Tuple[List[Tuple[str, dict]], float]:
    """
    Search for similar documents using semantic embeddings
    
    Args:
        query: User question/query
        top_k: Number of results to return
        threshold: Minimum similarity score (0-1 scale)
    
    Returns:
        Tuple of ([(text, metadata), ...], confidence_score)
        - text: Document chunk text
        - metadata: Dict with source, page, similarity score
        - confidence_score: Best match score
    """
    
    if _embeddings is None or len(_documents) == 0:
        print("⚠️ Vector store not initialized. Call initialize_vector_store() first.")
        return [], 0.0
    
    # Embed the query
    query_embedding = _model.encode([query], normalize_embeddings=True)[0]
    query_embedding = np.array([query_embedding]).astype("float32")
    
    # Compute similarity scores (cosine similarity with normalized vectors)
    similarities = np.dot(_embeddings, query_embedding.T).flatten()
    
    # Get top_k results
    top_indices = np.argsort(similarities)[::-1][:top_k]
    top_similarities = similarities[top_indices]
    
    # Check if all results are below threshold
    if top_similarities[0] < threshold:
        print(f"⚠️ Low confidence: {top_similarities[0]:.3f} (threshold: {threshold})")
        return [], float(top_similarities[0])
    
    # Return matching documents with metadata
    results = [
        (
            _documents[idx]['text'],
            {
                'source': _documents[idx].get('source', 'unknown'),
                'page': _documents[idx].get('page', 'unknown'),
                'similarity': float(top_similarities[i]),
                'chunk_id': _documents[idx].get('chunk_id', '')
            }
        )
        for i, idx in enumerate(top_indices)
    ]
    
    return results, float(top_similarities[0])


# For backward compatibility (if your code calls this)
def search_old_format(query: str, top_k: int = 3) -> Tuple[List[Tuple[str, float]], float]:
    """
    Backward compatible search (returns old format with just text and score)
    """
    results, confidence = search(query, top_k)
    
    # Convert to old format if needed
    old_results = [(text, meta['similarity']) for text, meta in results]
    
    return old_results, confidence

