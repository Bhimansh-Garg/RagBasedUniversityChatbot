import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Dict

JSON_FOLDER = "json_embeddings"

# ============ GLOBAL STATE ============

_json_data = None
_json_embeddings = None
_json_texts = None
_model = None

def initialize_json_store(rebuild: bool = False):
    """
    Initialize JSON embeddings store
    Loads all JSON files and generates embeddings for Q&A pairs
    
    Call this ONCE in app.py startup
    """
    global _json_data, _json_embeddings, _json_texts, _model
    
    # Load embedding model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✓ Model loaded")
    
    # Load all JSON files
    print(f"Loading JSON embeddings from {JSON_FOLDER}...")
    _json_data = []
    _json_texts = []
    
    if not os.path.exists(JSON_FOLDER):
        print(f"⚠️ {JSON_FOLDER} folder not found!")
        return
    
    # Load each JSON file
    json_files = [f for f in os.listdir(JSON_FOLDER) if f.endswith('.json')]
    
    for json_file in json_files:
        filepath = os.path.join(JSON_FOLDER, json_file)
        print(f"  Processing: {json_file}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract Q&A pairs from different JSON structures
            qa_pairs = extract_qa_pairs(data, json_file)
            _json_data.extend(qa_pairs)
            
            print(f"    ✓ Extracted {len(qa_pairs)} Q&A pairs")
            
        except Exception as e:
            print(f"    ✗ Error reading {json_file}: {e}")
    
    if not _json_data:
        print("⚠️ No Q&A pairs found in JSON files!")
        return
    
    # Generate embeddings
    print(f"\nGenerating embeddings for {len(_json_data)} Q&A pairs...")
    
    # Use question + answer for embedding (better context)
    for item in _json_data:
        combined_text = f"{item['question']} {item['answer']}"
        _json_texts.append(combined_text)
    
    # Generate embeddings
    _json_embeddings = _model.encode(_json_texts, normalize_embeddings=True, show_progress_bar=True)
    _json_embeddings = np.array(_json_embeddings).astype("float32")
    
    print(f"✓ Embeddings generated. Shape: {_json_embeddings.shape}")
    print(f"✅ JSON store initialized with {len(_json_data)} Q&A pairs")


def extract_qa_pairs(data: dict, source_file: str) -> List[Dict]:
    """
    Extract Q&A pairs from different JSON structures
    Handles all 4 JSON file formats
    """
    qa_pairs = []
    
    # Structure 1: embeddings.institution_overview (nested)
    if "embeddings" in data:
        for category_name, category_data in data["embeddings"].items():
            if isinstance(category_data, dict) and "entries" in category_data:
                for entry in category_data["entries"]:
                    qa_pairs.append({
                        'question': entry.get('question', ''),
                        'answer': entry.get('answer', ''),
                        'category': category_data.get('name', category_name),
                        'id': entry.get('id', ''),
                        'source': source_file,
                        'keywords': entry.get('keywords', [])
                    })
    
    # Structure 2: institution_info (flat list)
    elif "institution_info" in data:
        for entry in data.get("institution_info", []):
            qa_pairs.append({
                'question': entry.get('question', ''),
                'answer': entry.get('answer', ''),
                'category': entry.get('category', 'General'),
                'id': entry.get('id', ''),
                'source': source_file,
                'keywords': []
            })
    
    # Structure 3: Multiple categories (academic_programs, admissions, etc.)
    else:
        for key, items in data.items():
            if isinstance(items, list):
                for entry in items:
                    if isinstance(entry, dict) and 'question' in entry:
                        qa_pairs.append({
                            'question': entry.get('question', ''),
                            'answer': entry.get('answer', ''),
                            'category': entry.get('category', key),
                            'id': entry.get('id', ''),
                            'source': source_file,
                            'keywords': entry.get('keywords', [])
                        })
    
    # Structure 4: personnel_qa_embeddings (nested)
    if "personnel_qa_embeddings" in data:
        for section_name, section_data in data["personnel_qa_embeddings"].items():
            if section_name == "metadata":
                continue
            
            if isinstance(section_data, list):
                for entry in section_data:
                    qa_pairs.append({
                        'question': entry.get('question', ''),
                        'answer': entry.get('answer', ''),
                        'category': entry.get('category', section_name),
                        'id': entry.get('id', ''),
                        'source': source_file,
                        'keywords': entry.get('keywords', [])
                    })
    
    return qa_pairs


def search_json(query: str, top_k: int = 3, threshold: float = 0.80) -> Tuple[List[Tuple[str, Dict]], float]:
    """
    Search JSON embeddings with high confidence threshold
    
    Args:
        query: User question
        top_k: Number of results to return
        threshold: Minimum similarity score (0-1)
    
    Returns:
        Tuple of ([(answer_text, metadata), ...], best_confidence)
    """
    
    if _json_embeddings is None or len(_json_data) == 0:
        print("⚠️ JSON store not initialized. Call initialize_json_store() first.")
        return [], 0.0
    
    # Embed query
    query_embedding = _model.encode([query], normalize_embeddings=True)[0]
    query_embedding = np.array([query_embedding]).astype("float32")
    
    # Compute similarities
    similarities = np.dot(_json_embeddings, query_embedding.T).flatten()
    
    # Get top results
    top_indices = np.argsort(similarities)[::-1][:top_k]
    top_scores = similarities[top_indices]
    
    # Check threshold
    if top_scores[0] < threshold:
        print(f"⚠️ JSON: Low confidence {top_scores[0]:.3f} (need >{threshold})")
        return [], float(top_scores[0])
    
    # Build results
    results = []
    for i, idx in enumerate(top_indices):
        item = _json_data[idx]
        results.append((
            item['answer'],
            {
                'source': item['source'],
                'category': item.get('category', 'General'),
                'question': item['question'],
                'similarity': float(top_scores[i]),
                'id': item.get('id', '')
            }
        ))
    
    return results, float(top_scores[0])


def get_json_stats() -> Dict:
    """Get statistics about loaded JSON data"""
    if _json_data is None:
        return {"status": "not_initialized"}
    
    categories = {}
    for item in _json_data:
        cat = item.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_qa_pairs": len(_json_data),
        "categories": categories,
        "embedding_shape": tuple(_json_embeddings.shape) if _json_embeddings is not None else None,
        "status": "initialized"
    }


if __name__ == "__main__":
    # Test
    initialize_json_store()
    
    test_queries = [
        "who is director of nit jalandhar",
        "what is placement rate",
        "btech admission process"
    ]
    
    for query in test_queries:
        results, conf = search_json(query)
        print(f"\nQuery: {query}")
        print(f"Confidence: {conf:.3f}")
        if results:
            for answer, meta in results:
                print(f"  Category: {meta['category']}")
                print(f"  Answer: {answer[:150]}...")