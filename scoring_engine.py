# scoring_engine.py

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai
import os
import json

# ------------------------------
# Setup Gemini
# ------------------------------
BASE_DIR = Path(__file__).resolve().parent

import streamlit as st

API_KEY = st.secrets["GEMINI_API_KEY"]


if not API_KEY:
    raise ValueError("❌ Missing GEMINI_API_KEY in .env for scoring_engine")

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")


TRAITS = [
    "discipline",
    "consistency",
    "execution",
    "adaptability",
    "ego_strength",
    "clarity",
]


SCORING_SYSTEM_PROMPT = """
You are a hybrid evaluation engine combining:
- Jinpachi Ego (Blue Lock): ruthless performance standards
- Ayanokoji (Classroom of the Elite): cold, logical analysis
- Johan (Monster, ethical): deep psychological insight
- Tokuchi Toua (One Outs): strategic, risk-reward reasoning

Your job is to evaluate a user's current competitive mindset,
based on:
- What they say (their message)
- How the agent responds
- Their existing scores (if given)

You must output NUMERIC SCORES for these traits (0–100):
- discipline
- consistency
- execution
- adaptability
- ego_strength
- clarity

0 = extremely weak / self-sabotaging
50 = average / unstable
100 = elite world-class mindset

Be strict like Jinpachi Ego, analytical like Ayanokoji,
insightful like Johan, strategic like Tokuchi.

IMPORTANT:
- Do NOT be nice. Be accurate and harsh.
- Use their wording, fears, excuses, and ambition to judge.
- If they show excuses or vagueness, lower discipline/clarity.
- If they show ambition and willingness to act, increase ego_strength and execution.
- If they show flexibility, increase adaptability.
- If they show consistent action, increase consistency.

Your output MUST be ONLY valid JSON in this shape:

{
  "scores": {
    "discipline": <number>,
    "consistency": <number>,
    "execution": <number>,
    "adaptability": <number>,
    "ego_strength": <number>,
    "clarity": <number>
  },
  "notes": {
    "discipline": "<short note>",
    "consistency": "<short note>",
    "execution": "<short note>",
    "adaptability": "<short note>",
    "ego_strength": "<short note>",
    "clarity": "<short note>"
  }
}

No extra commentary, no markdown, no text outside JSON.
"""


def _safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)


def infer_scores(
    user_message: str,
    agent_reply: str,
    current_scores: Dict[str, float] | None = None,
) -> Dict[str, float]:
    """
    Ask Gemini to infer updated scores for the user's mindset traits
    based on the latest interaction.
    """
    if current_scores is None:
        current_scores = {t: 0.0 for t in TRAITS}

    prompt = f"""
{SCORING_SYSTEM_PROMPT}

### USER MESSAGE:
{user_message}

### AGENT REPLY:
{agent_reply}

### CURRENT SCORES (for reference, may be empty or all zeros):
{json.dumps(current_scores)}
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # Try to parse JSON safely
    data: Dict[str, Any] = {}
    try:
        # If model wrapped JSON in extra text, try to extract {...}
        if not raw.startswith("{"):
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                raw = raw[start : end + 1]
        data = json.loads(raw)
    except Exception:
        # Fallback: return current scores unchanged
        return current_scores

    new_scores: Dict[str, float] = {}
    scores_block = data.get("scores", {})

    for t in TRAITS:
        val = scores_block.get(t, current_scores.get(t, 0.0))
        new_scores[t] = max(0.0, min(100.0, _safe_float(val, current_scores.get(t, 0.0))))

    return new_scores
