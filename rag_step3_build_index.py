# rag_step3_build_index.py

import json
from pathlib import Path

import numpy as np
import faiss

# ======================================
#              PATHS
# ======================================

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "Knowledge_base"

EMBED_FILE = KB_DIR / "embeddings.jsonl"
INDEX_FILE = KB_DIR / "faiss_index.bin"
META_FILE = KB_DIR / "faiss_meta.jsonl"

print("\n=== PATH DEBUG ===")
print("BASE_DIR:", BASE_DIR)
print("KB_DIR:", KB_DIR)
print("EMBED_FILE exists?", EMBED_FILE.exists())


# ======================================
#      LOAD EMBEDDINGS + METADATA
# ======================================

embeddings = []
metas = []

print("\n=== Loading embeddings from JSONL ===")

with open(EMBED_FILE, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue

        obj = json.loads(line)

        emb = obj["embedding"]
        embeddings.append(emb)

        metas.append({
            "id": obj["id"],
            "source": obj["source"],
            "content": obj["content"],
        })

print(f"Total vectors loaded: {len(embeddings)}")

if not embeddings:
    raise ValueError("❌ No embeddings found. Did you run rag_step2_embed.py?")


# ======================================
#      CONVERT TO NUMPY ARRAY
# ======================================

emb_array = np.array(embeddings, dtype="float32")
print("Embedding matrix shape:", emb_array.shape)  # (N, D)

# Normalize for cosine similarity
norms = np.linalg.norm(emb_array, axis=1, keepdims=True) + 1e-12
emb_array = emb_array / norms


# ======================================
#      BUILD FAISS INDEX (cosine via IP)
# ======================================

dim = emb_array.shape[1]
print("Embedding dimension:", dim)

index = faiss.IndexFlatIP(dim)  # Inner product (after normalization = cosine)
index.add(emb_array)

print("FAISS index total vectors:", index.ntotal)


# ======================================
#      SAVE INDEX + METADATA
# ======================================

faiss.write_index(index, str(INDEX_FILE))
print("\n✅ Saved FAISS index to:", INDEX_FILE)

with open(META_FILE, "w", encoding="utf-8") as f:
    for m in metas:
        f.write(json.dumps(m, ensure_ascii=False) + "\n")

print("✅ Saved metadata to:", META_FILE)

print("\n🎉 DONE: Vector index + metadata are ready.")
