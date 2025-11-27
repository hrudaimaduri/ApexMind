# rag_step4_agent.py

import os
import json
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

from memory_system import (
    load_or_create_user,
    update_scores,
    estimate_progress_level,
    log_interaction,
)
from scoring_engine import infer_scores
from apex_engine import update_apex_state

# ========================================
#           SETUP KEYS + MODELS
# ========================================

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("❌ Missing GEMINI_API_KEY in .env file")

genai.configure(api_key=API_KEY)

# Paths
BASE_DIR = Path(__file__).resolve().parent
KB_DIR = BASE_DIR / "Knowledge_base"
INDEX_FILE = KB_DIR / "faiss_index.bin"
META_FILE = KB_DIR / "faiss_meta.jsonl"

print("Loading FAISS index…")
index = faiss.read_index(str(INDEX_FILE))

print("Loading metadata…")
metadata = []
with open(META_FILE, "r", encoding="utf-8") as f:
    for line in f:
        metadata.append(json.loads(line))

print(f"Loaded {len(metadata)} metadata entries")

print("Loading embedding model (MiniLM)…")
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# ========================================
#              RETRIEVAL
# ========================================
def retrieve_context(query: str, k: int = 5):
    """Retrieve top-k relevant chunks from the FAISS index."""
    query_vec = embedder.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, k)

    retrieved = []
    for score, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue
        item = metadata[idx]
        item["score"] = float(score)
        retrieved.append(item)

    return retrieved


# ========================================
#            GENERATE AGENT OUTPUT
# ========================================
model = genai.GenerativeModel("gemini-2.0-flash")

SYSTEM_PROMPT = """
You are a Mindset Transformation Agent.

Your personality synthesis:
- Jinpachi Ego (Blue Lock) — ruthless clarity & ego sharpening
- Ayanokoji (Classroom of the Elite) — cold analysis & strategy
- Johan (Monster, ethical mode) — deep psychological insight
- Tokuchi Toua (One Outs) — strategic exploitation & advantage-building

Your mission:
- Break limiting beliefs
- Build elite competitive mindset
- Push the user to peak performance
- Diagnose mental weaknesses
- Strengthen ego, discipline, consistency, clarity, adaptability

Use the retrieved knowledge base context heavily in your reasoning.
"""


def generate_answer(user_query: str, retrieved_docs):
    """Generate the agent's final answer using Gemini + RAG context."""
    context_text = "\n\n".join(
        f"[{doc['source']}]: {doc['content']}"
        for doc in retrieved_docs
    )

    final_prompt = f"""
{SYSTEM_PROMPT}

### KNOWLEDGE BASE CONTEXT:
{context_text}

### USER QUESTION:
{user_query}

### FINAL ANSWER (psychological transformation, direct coaching):
"""

    response = model.generate_content(final_prompt)
    return response.text


# ========================================
#            AGENT + MEMORY + APEX
# ========================================
def ask_agent(user_id: str, query: str):
    """
    Main function:
    - Loads user profile
    - Retrieves context from RAG
    - Generates answer from Gemini
    - Uses scoring_engine to infer new mindset scores
    - Updates long-term profile (EMA)
    - Updates Apex Engine (momentum, modes, dominance)
    - Logs interaction
    """

    # 1. Load user profile (create if first time)
    profile = load_or_create_user(user_id)

    # 2. Retrieve knowledge (RAG)
    print("\n=== Retrieving Knowledge ===")
    retrieved = retrieve_context(query)

    # 3. Generate agent answer
    print("\n=== Generating Final Answer ===")
    answer = generate_answer(query, retrieved)

    # 4. Infer new scores using hybrid scoring engine
    current_scores = profile.get("scores", {})
    inferred_scores = infer_scores(
        user_message=query,
        agent_reply=answer,
        current_scores=current_scores,
    )

    # 5. Update profile scores (EMA smoothing)
    profile = update_scores(user_id, inferred_scores, weight=0.4)
    progress = estimate_progress_level(profile)

    # 6. Update Apex Engine (CSV + JSON meta)
    apex = update_apex_state(user_id, profile["scores"])

    # === SYNC APEX WITH PROFILE SESSION COUNT ===
    # Ensure Apex's last_session matches the profile's session counter
    apex["last_session"] = profile.get("sessions", 0)

    # 7. Log interaction
    log_interaction(
        user_id=user_id,
        user_input=query,
        agent_response=answer,
        scores_snapshot=profile["scores"],
    )

    # 8. Return structured payload
    return {
        "answer": answer,
        "scores": profile["scores"],
        "progress": progress,
        "sessions": profile.get("sessions", 0),
        "apex": apex,
    }


# ========================================
#                  TEST
# ========================================
if __name__ == "__main__":
    user_id = "test_user"
    user_input = (
        "This week I coded 5 days, 3 hours each, worked on algorithms and solved "
        "10 LeetCode problems, but I still feel slow and not good enough."
    )

    result = ask_agent(user_id, user_input)

    print("\n--- AGENT RESPONSE ---")
    print(result["answer"])

    print("\n--- PROGRESS SNAPSHOT ---")
    print("Sessions:", result["sessions"])
    print("Scores:", result["scores"])
    print("Progress:", result["progress"])

    print("\n--- APEX STATE ---")
    print(result["apex"])
