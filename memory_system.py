# memory_system.py

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parent
USER_DIR = BASE_DIR / "user_data"
USER_DIR.mkdir(exist_ok=True)


# -----------------------------
# Helpers
# -----------------------------
def _user_profile_path(user_id: str) -> Path:
    return USER_DIR / f"{user_id}_profile.json"


def _user_log_path(user_id: str) -> Path:
    return USER_DIR / f"{user_id}_log.jsonl"


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


# -----------------------------
# User Profile Management
# -----------------------------
def load_or_create_user(user_id: str) -> Dict[str, Any]:
    """
    Load user profile if exists, else create a new one.
    """
    path = _user_profile_path(user_id)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # New user skeleton
    profile = {
        "user_id": user_id,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "goals": [],  # list of {id, text, category, created_at}
        "scores": {   # all 0–100
            "discipline": 0.0,
            "consistency": 0.0,
            "execution": 0.0,
            "adaptability": 0.0,
            "ego_strength": 0.0,
            "clarity": 0.0,
        },
        "sessions": 0,   # number of coaching interactions
    }

    save_user_profile(profile)
    return profile


def save_user_profile(profile: Dict[str, Any]) -> None:
    profile["updated_at"] = _now_iso()
    path = _user_profile_path(profile["user_id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile, f, ensure_ascii=False, indent=2)


def add_goal(
    user_id: str,
    goal_text: str,
    category: str = "general"
) -> Dict[str, Any]:
    """
    Append a new goal to the user's profile.
    """
    profile = load_or_create_user(user_id)
    goal_id = f"goal-{len(profile['goals']) + 1}"

    goal = {
        "id": goal_id,
        "text": goal_text,
        "category": category,
        "created_at": _now_iso(),
    }
    profile["goals"].append(goal)
    save_user_profile(profile)
    return goal


# -----------------------------
# Progress / Score Updating
# -----------------------------
def update_scores(
    user_id: str,
    new_scores: Dict[str, float],
    weight: float = 0.3,
) -> Dict[str, Any]:
    """
    Update running average scores for the user.
    new_scores: e.g. {"discipline": 80, "consistency": 60, ...}
    weight: how much to weight the new scores vs old (0–1)
    """
    profile = load_or_create_user(user_id)
    scores = profile.get("scores", {})

    for key, new_val in new_scores.items():
        if key not in scores:
            continue
        old_val = scores.get(key, 0.0)
        # exponential moving average
        scores[key] = (1 - weight) * old_val + weight * float(new_val)

    profile["scores"] = scores
    profile["sessions"] = profile.get("sessions", 0) + 1
    save_user_profile(profile)
    return profile


def estimate_progress_level(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple heuristic to describe progress:
    - avg_score
    - tier label
    """
    scores = profile.get("scores", {})
    if not scores:
        return {"avg_score": 0, "tier": "Unrated"}

    vals = list(scores.values())
    avg = sum(vals) / len(vals)

    if avg < 30:
        tier = "Novice (far from potential)"
    elif avg < 50:
        tier = "Developing (early grind phase)"
    elif avg < 70:
        tier = "Serious Competitor"
    elif avg < 85:
        tier = "High Performer"
    else:
        tier = "Elite Trajectory"

    return {"avg_score": avg, "tier": tier}


# -----------------------------
# Interaction Logging
# -----------------------------
def log_interaction(
    user_id: str,
    user_input: str,
    agent_response: str,
    scores_snapshot: Optional[Dict[str, float]] = None,
) -> None:
    """
    Append a log line with what happened in a coaching interaction.
    """
    log_path = _user_log_path(user_id)
    record = {
        "timestamp": _now_iso(),
        "user_input": user_input,
        "agent_response": agent_response,
        "scores": scores_snapshot,
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_recent_history(
    user_id: str,
    limit: int = 10,
) -> list[Dict[str, Any]]:
    """
    Load last N interactions for reflection or meta-coaching.
    """
    log_path = _user_log_path(user_id)
    if not log_path.exists():
        return []

    lines = log_path.read_text(encoding="utf-8").splitlines()
    recent = lines[-limit:]
    return [json.loads(x) for x in recent]
