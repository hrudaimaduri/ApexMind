# rag_step2_embed.py

import json
from pathlib import Path
from dotenv import load_dotenv
import os

# Load chunk loader from Step 1
from rag_step1_load_data import load_knowledge_base

# FREE & LOCAL embedding model
from sentence_transformers import SentenceTransformer


# ======================================
#           LOAD ENVIRONMENT
# ======================================

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("⚠ INFO: GEMINI_API_KEY missing — embeddings do NOT use Gemini.")
    print("         This is normal. SentenceTransformer runs offline.\n")


# ======================================
#              PATHS
# ======================================

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "Knowledge_base"
EMBED_FILE = KB_DIR / "embeddings.jsonl"


# ======================================
#        LOAD CHUNKS FROM STEP 1
# ======================================

print("\n=== Loading Knowledge Base Chunks ===")
chunks = load_knowledge_base()
print(f"Total chunks loaded: {len(chunks)}")


# ======================================
#          EMBEDDING MODEL
# ======================================

print("\n=== Loading Embedding Model (SentenceTransformer) ===")
model = SentenceTransformer("all-MiniLM-L6-v2")   # 384d embeddings
print("Embedding model loaded!\n")


def embed_text(text: str):
    """Create a vector embedding from text."""
    return model.encode(text).tolist()


# ======================================
#      GENERATE + SAVE EMBEDDINGS
# ======================================

print("=== Generating Embeddings ===")

with open(EMBED_FILE, "w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunks, start=1):
        vector = embed_text(chunk["content"])

        item = {
            "id": i,
            "source": chunk["source"],
            "content": chunk["content"],
            "embedding": vector,
        }

        f.write(json.dumps(item) + "\n")

        print(f"Embedded chunk {i}/{len(chunks)}")


print(f"\n🎉 DONE! Embeddings saved to:")
print(EMBED_FILE)
