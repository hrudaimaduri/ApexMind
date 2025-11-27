# rag_step1_load_data.py

from pathlib import Path
from typing import List, Dict


# ======================================
#           PATH SETUP
# ======================================

BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "Knowledge_base"

print("\n=== PATH DEBUG ===")
print("BASE_DIR =", BASE_DIR)
print("KB_DIR =", KB_DIR)
print("Exists?", KB_DIR.exists())


# ======================================
#           CHUNKING FUNCTION
# ======================================

def chunk_text(
    text: str,
    source: str,
    max_chars: int = 800,
    overlap: int = 150
) -> List[Dict]:

    chunks: List[Dict] = []
    text = text.strip()

    if not text:
        return chunks

    # Overlap safety
    overlap = min(overlap, max_chars - 1)

    start = 0
    length = len(text)

    while start < length:

        end = min(length, start + max_chars)
        chunk = text[start:end].strip()

        if chunk:
            chunks.append({
                "source": source,
                "content": chunk
            })

        # SAFE movement forward
        new_start = end - overlap

        if new_start <= start:
            # Prevent infinite loop
            new_start = start + max_chars

        start = new_start

    return chunks


# ======================================
#      LOAD KNOWLEDGE BASE FILES
# ======================================

def load_knowledge_base() -> List[Dict]:
    chunks: List[Dict] = []

    print("\n=== FILES DETECTED IN KNOWLEDGE BASE ===")
    files = list(KB_DIR.glob("*.txt"))

    if not files:
        print("⚠ No .txt files found!")
        return chunks

    for txt in files:
        print(f"\nLoading: {txt.name}")
        print("Full path:", txt.resolve())

        try:
            with open(txt, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print("ERROR reading file:", e)
            continue

        print("File size:", len(text), "characters")

        # Chunk file text
        text_chunks = chunk_text(text, txt.name)
        print("->", len(text_chunks), "chunks created")

        chunks.extend(text_chunks)

    return chunks


# ======================================
#              MAIN TEST
# ======================================

if __name__ == "__main__":
    chunks = load_knowledge_base()

    print("\n=== SAMPLE CHUNKS (3) ===")

    for c in chunks[:3]:
        print("\n---")
        print("Source:", c["source"])
        print(c["content"][:300], "...")
