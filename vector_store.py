import faiss
from sentence_transformers import SentenceTransformer
from data_loader import load_documents

model = SentenceTransformer("all-MiniLM-L6-v2")
documents = load_documents()
embeddings = model.encode(documents)

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

def search(query, top_k=3):
    query_vector = model.encode([query], normalize_embeddings=True)
    scores, indices = index.search(query_vector, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if score > 0.35:
            results.append(documents[idx])

    return results   # ALWAYS a list

