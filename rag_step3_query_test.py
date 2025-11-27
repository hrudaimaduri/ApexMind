# rag_step3_query_test.py

import json
from pathlib import Path

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


# ======================================
#              PATHS
# ======================================

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "Knowledge_base"

INDEX_FILE = KB_DIR / "faiss_index.bin"
META_FILE = KB_DIR / "faiss_meta.jsonl"

print("\n=== PATH DEBUG ===")
print("BASE_DIR:", BASE_DIR)
print("KB_DIR:", KB_DIR)
print("INDEX_FILE exists?", INDEX_FILE.exists())
print("META_FILE exists?", META_FILE.exists())


# ======================================
#     LOAD FAISS INDEX + METADATA
# ======================================

index = faiss.read_index(str(INDEX_FILE))

metas = []
with open(META_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        metas.append(json.loads(line))

print("Loaded metadata entries:", len(metas))


# ======================================
#        LOAD EMBEDDING MODEL
# ======================================

print("\n=== Loading SentenceTransformer model ===")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded!")


def embed_query(text: str) -> np.ndarray:
    vec = model.encode(text)
    # normalize for cosine similarity
    vec = vec.astype("float32")
    vec = vec / (np.linalg.norm(vec) + 1e-12)
    return vec.reshape(1, -1)


def search_knowledge(query: str, top_k: int = 5):
    print(f"\n=== QUERY: {query} ===")
    q_emb = embed_query(query)
    scores, indices = index.search(q_emb, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        meta = metas[idx]
        results.append({
            "score": float(score),
            "source": meta["source"],
            "content": meta["content"]
        })

    return results


if __name__ == "__main__":
    # Example test
    query = "How do I develop an ego like Blue Lock and become highly competitive?"
    results = search_knowledge(query, top_k=3)

    print("\n=== TOP RESULTS ===")
    for i, r in enumerate(results, start=1):
        print(f"\n--- Result {i} ---")
        print("Score:", r["score"])
        print("Source:", r["source"])
        print("Content snippet:", r["content"][:300], "...")
