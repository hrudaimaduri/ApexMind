# apex_engine.py

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import csv
import json
import math

# Traits we track
TRAITS = [
    "discipline",
    "consistency",
    "execution",
    "adaptability",
    "ego_strength",
    "clarity",
]

BASE_DIR = Path(__file__).resolve().parent
USER_DIR = BASE_DIR / "user_data"
USER_DIR.mkdir(exist_ok=True)


# ----------------------------
# Helpers
# ----------------------------
def _sessions_csv_path(user_id: str) -> Path:
    return USER_DIR / f"{user_id}_sessions.csv"


def _apex_meta_path(user_id: str) -> Path:
    return USER_DIR / f"{user_id}_apex_meta.json"


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _ensure_sessions_header(path: Path):
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["session", "timestamp"] + TRAITS)


# ----------------------------
# Session Recording
# ----------------------------
def append_session_row(
    user_id: str,
    session_idx: int,
    scores: Dict[str, float],
) -> None:
    csv_path = _sessions_csv_path(user_id)
    _ensure_sessions_header(csv_path)

    row = [session_idx, _now_iso()]
    for t in TRAITS:
        row.append(float(scores.get(t, 0.0)))

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def load_sessions(user_id: str) -> List[Dict[str, Any]]:
    csv_path = _sessions_csv_path(user_id)
    if not csv_path.exists():
        return []

    sessions: List[Dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            s: Dict[str, Any] = {
                "session": int(row["session"]),
                "timestamp": row["timestamp"],
            }
            for t in TRAITS:
                try:
                    s[t] = float(row.get(t, 0.0))
                except Exception:
                    s[t] = 0.0
            sessions.append(s)

    # Ensure sorted by session index
    sessions.sort(key=lambda x: x["session"])
    return sessions


# ----------------------------
# Metrics Calculations
# ----------------------------
def compute_momentum(sessions: List[Dict[str, Any]]) -> float:
    """
    Momentum = average positive delta across last few sessions.
    Range roughly [-1.0, 1.0]. We clip just in case.
    """
    if len(sessions) < 2:
        return 0.0

    # Use last up to 5 sessions
    recent = sessions[-5:]
    deltas = []

    for i in range(1, len(recent)):
        prev = recent[i - 1]
        curr = recent[i]
        for t in TRAITS:
            deltas.append(curr[t] - prev[t])

    if not deltas:
        return 0.0

    avg_delta = sum(deltas) / len(deltas)
    # Scale down: assume 0–100 scale, normalize to [-1, 1] approx
    momentum = max(-1.0, min(1.0, avg_delta / 25.0))
    return momentum


def compute_volatility(sessions: List[Dict[str, Any]]) -> float:
    """
    Volatility = how unstable the average trait score has been.
    0 = totally stable, higher = more unstable.
    """
    if len(sessions) < 2:
        return 0.0

    avg_scores = []
    for s in sessions:
        vals = [s[t] for t in TRAITS]
        avg_scores.append(sum(vals) / len(vals))

    mean = sum(avg_scores) / len(avg_scores)
    var = sum((x - mean) ** 2 for x in avg_scores) / len(avg_scores)
    # Normalize volatility to [0, 1]-ish range
    vol = math.sqrt(var) / 100.0
    return min(1.0, max(0.0, vol))


def compute_dominance_index(scores: Dict[str, float]) -> float:
    """
    Dominance index ~ how close you are to "top 1% competitor".
    Weighted combination of traits, 0.0–1.0.
    """
    weights = {
        "discipline": 1.2,
        "consistency": 1.3,
        "execution": 1.3,
        "adaptability": 1.0,
        "ego_strength": 1.4,
        "clarity": 1.0,
    }
    total_w = sum(weights.values())
    num = 0.0
    for t, w in weights.items():
        num += w * float(scores.get(t, 0.0))

    raw = num / (total_w * 100.0)  # 0–1
    return max(0.0, min(1.0, raw))


def determine_modes(scores: Dict[str, float], momentum: float) -> list[str]:
    modes: list[str] = []

    if scores.get("ego_strength", 0.0) >= 30:
        modes.append("Ego Ascension Mode")

    if scores.get("discipline", 0.0) >= 20 and scores.get("consistency", 0.0) >= 20:
        modes.append("Elite Routine Mode")

    if scores.get("clarity", 0.0) >= 15:
        modes.append("Strategic Clarity Mode")

    if momentum > 0.25:
        modes.append("Hypergrowth Mode")

    if not modes:
        modes.append("Foundational Grind Mode")

    return modes


def determine_focus_arc(scores: Dict[str, float]) -> Dict[str, Any]:
    """
    Decide which trait is currently holding the user back the most.
    """
    if not scores:
        return {"weak_trait": None, "arc": "No Data Yet"}

    # Find weakest trait
    weak_trait = min(scores, key=lambda k: scores.get(k, 0.0))

    arc_map = {
        "discipline": "Discipline Arc — daily structure, no escape routes.",
        "consistency": "Consistency Arc — remove zero days, build streaks.",
        "execution": "Execution Arc — more doing, less overthinking.",
        "adaptability": "Adaptability Arc — embrace chaos, adjust faster.",
        "ego_strength": "Ego Ascension Arc — rebuild identity around winning.",
        "clarity": "Clarity Arc — sharpen goals, eliminate vagueness.",
    }

    return {
        "weak_trait": weak_trait,
        "arc": arc_map.get(weak_trait, "General Growth Arc"),
    }


# ----------------------------
# APEX STATE UPDATE
# ----------------------------
def update_apex_state(user_id: str, scores: Dict[str, float]) -> Dict[str, Any]:
    """
    Called each session after scores are updated.
    - Append new row to CSV
    - Recompute metrics (momentum, volatility, dominance)
    - Determine modes + focus arc
    - Save to JSON meta
    - Return all metrics
    """
    # 1. Load existing sessions to infer current session index
    sessions = load_sessions(user_id)
    next_session_idx = (sessions[-1]["session"] + 1) if sessions else 1

    # 2. Append new session row
    append_session_row(user_id, next_session_idx, scores)

    # 3. Reload with the new row included
    sessions = load_sessions(user_id)

    # 4. Compute metrics
    momentum = compute_momentum(sessions)
    volatility = compute_volatility(sessions)
    dominance_index = compute_dominance_index(scores)
    modes = determine_modes(scores, momentum)
    focus_arc = determine_focus_arc(scores)

    apex = {
        "user_id": user_id,
        "last_session": next_session_idx,
        "momentum": momentum,
        "volatility": volatility,
        "dominance_index": dominance_index,
        "modes": modes,
        "focus_arc": focus_arc,
        "updated_at": _now_iso(),
    }

    # 5. Save meta for later inspection / dashboards
    meta_path = _apex_meta_path(user_id)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(apex, f, ensure_ascii=False, indent=2)

    return apex
