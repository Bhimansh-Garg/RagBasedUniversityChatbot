import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from data_loader import load_documents

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load documents
documents = load_documents()

# Create document embeddings (normalized for cosine similarity)
embeddings = model.encode(documents, normalize_embeddings=True)

# Convert to float32 (FAISS requires this)
embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]

# Use Inner Product index for cosine similarity
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

def search(query, top_k=3):
    # Encode query
    query_vector = model.encode([query], normalize_embeddings=True)
    query_vector = np.array(query_vector).astype("float32")

    # Search
    scores, indices = index.search(query_vector, top_k)

    results = []
    best_score = 0

    best_score = scores[0][0]

    for score, idx in zip(scores[0], indices[0]):
        if score > best_score * 0.80:   # only keep chunks close to best
            results.append((documents[idx], float(score)))


    return results, best_score
