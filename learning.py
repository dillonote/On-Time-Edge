"""
Learning module for the On Time Edge Copy Bot.

Gives the bot a memory: every generation is logged, users can rate
outputs, and the system adapts over time — weighting template variants
toward what works and injecting top-performing examples into LLM prompts.

Storage: SQLite (stdlib, zero extra dependencies).
"""

import json
import os
import sqlite3
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

DB_PATH = os.getenv("OTE_LEARNING_DB", "ote_learning.db")

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
SCHEMA = """
CREATE TABLE IF NOT EXISTS generations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at  REAL    NOT NULL,
    asset_type  TEXT    NOT NULL,
    request     TEXT    NOT NULL,   -- JSON of the full OTECopyRequest
    response    TEXT    NOT NULL,   -- JSON of the full OTECopyResponse
    slippery    REAL    NOT NULL,
    -- Variant tracking (which template choices were made)
    variant_key TEXT,               -- e.g. "email_single|subject:2|opener:0|bridge:1"
    -- Feedback (filled in later via /feedback)
    rating      INTEGER,            -- 1-5, NULL until rated
    feedback    TEXT,               -- free-text user notes
    rated_at    REAL                -- timestamp of rating
);

CREATE INDEX IF NOT EXISTS idx_gen_asset   ON generations(asset_type);
CREATE INDEX IF NOT EXISTS idx_gen_rating  ON generations(rating);
CREATE INDEX IF NOT EXISTS idx_gen_variant ON generations(variant_key);
"""


@contextmanager
def _db():
    """Yield a sqlite3 connection with WAL mode for concurrent reads."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist."""
    with _db() as conn:
        conn.executescript(SCHEMA)


# Auto-init on import
init_db()


# ---------------------------------------------------------------------------
# Logging generations
# ---------------------------------------------------------------------------
def log_generation(
    asset_type: str,
    request_dict: Dict[str, Any],
    response_dict: Dict[str, Any],
    slippery_score: float,
    variant_key: Optional[str] = None,
) -> int:
    """Log a generation and return its ID."""
    with _db() as conn:
        cur = conn.execute(
            """
            INSERT INTO generations (created_at, asset_type, request, response, slippery, variant_key)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                time.time(),
                asset_type,
                json.dumps(request_dict, ensure_ascii=False),
                json.dumps(response_dict, ensure_ascii=False),
                slippery_score,
                variant_key,
            ),
        )
        return cur.lastrowid


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------
def record_feedback(
    generation_id: int,
    rating: int,
    feedback_text: Optional[str] = None,
) -> bool:
    """Attach a 1-5 rating (and optional notes) to a generation. Returns True if found."""
    rating = max(1, min(5, rating))
    with _db() as conn:
        cur = conn.execute(
            """
            UPDATE generations
            SET rating = ?, feedback = ?, rated_at = ?
            WHERE id = ?
            """,
            (rating, feedback_text, time.time(), generation_id),
        )
        return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Variant performance — used by _pick() to prefer winners
# ---------------------------------------------------------------------------
def variant_scores(asset_type: str) -> Dict[str, float]:
    """
    Return {variant_key: avg_rating} for all rated generations of a given
    asset type.  Only includes variants with 2+ ratings so a single
    outlier doesn't dominate.
    """
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT variant_key, AVG(rating) as avg_rating, COUNT(*) as n
            FROM generations
            WHERE asset_type = ? AND rating IS NOT NULL AND variant_key IS NOT NULL
            GROUP BY variant_key
            HAVING n >= 2
            """,
            (asset_type,),
        ).fetchall()
    return {row["variant_key"]: row["avg_rating"] for row in rows}


# ---------------------------------------------------------------------------
# Top examples — used for few-shot learning in LLM prompts
# ---------------------------------------------------------------------------
def top_examples(
    asset_type: str,
    limit: int = 3,
    min_rating: int = 4,
) -> List[Dict[str, Any]]:
    """
    Return the highest-rated generations for an asset type, suitable for
    inclusion as few-shot examples in LLM prompts.
    """
    with _db() as conn:
        rows = conn.execute(
            """
            SELECT request, response, slippery, rating
            FROM generations
            WHERE asset_type = ? AND rating >= ?
            ORDER BY rating DESC, slippery DESC
            LIMIT ?
            """,
            (asset_type, min_rating, limit),
        ).fetchall()

    examples = []
    for row in rows:
        examples.append(
            {
                "request": json.loads(row["request"]),
                "response": json.loads(row["response"]),
                "slippery_score": row["slippery"],
                "rating": row["rating"],
            }
        )
    return examples


# ---------------------------------------------------------------------------
# Insights — what's working, what's not
# ---------------------------------------------------------------------------
def get_insights() -> Dict[str, Any]:
    """Aggregate learning data into actionable insights."""
    with _db() as conn:
        total = conn.execute("SELECT COUNT(*) as n FROM generations").fetchone()["n"]
        rated = conn.execute(
            "SELECT COUNT(*) as n FROM generations WHERE rating IS NOT NULL"
        ).fetchone()["n"]

        avg_rating = None
        if rated:
            avg_rating = conn.execute(
                "SELECT AVG(rating) as avg FROM generations WHERE rating IS NOT NULL"
            ).fetchone()["avg"]

        avg_slippery = conn.execute(
            "SELECT AVG(slippery) as avg FROM generations"
        ).fetchone()["avg"]

        # Per asset type breakdown
        by_asset = conn.execute(
            """
            SELECT asset_type,
                   COUNT(*) as total,
                   SUM(CASE WHEN rating IS NOT NULL THEN 1 ELSE 0 END) as rated,
                   AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating,
                   AVG(slippery) as avg_slippery
            FROM generations
            GROUP BY asset_type
            ORDER BY total DESC
            """
        ).fetchall()

        # Top performing variants
        top_variants = conn.execute(
            """
            SELECT variant_key, asset_type,
                   AVG(rating) as avg_rating, COUNT(*) as n
            FROM generations
            WHERE rating IS NOT NULL AND variant_key IS NOT NULL
            GROUP BY variant_key
            HAVING n >= 2
            ORDER BY avg_rating DESC
            LIMIT 10
            """
        ).fetchall()

        # Bottom performing variants (to avoid)
        bottom_variants = conn.execute(
            """
            SELECT variant_key, asset_type,
                   AVG(rating) as avg_rating, COUNT(*) as n
            FROM generations
            WHERE rating IS NOT NULL AND variant_key IS NOT NULL
            GROUP BY variant_key
            HAVING n >= 2
            ORDER BY avg_rating ASC
            LIMIT 5
            """
        ).fetchall()

        # Recent feedback
        recent = conn.execute(
            """
            SELECT id, asset_type, rating, feedback, rated_at
            FROM generations
            WHERE rating IS NOT NULL
            ORDER BY rated_at DESC
            LIMIT 10
            """
        ).fetchall()

    return {
        "total_generations": total,
        "total_rated": rated,
        "feedback_rate": round(rated / total * 100, 1) if total else 0,
        "avg_rating": round(avg_rating, 2) if avg_rating else None,
        "avg_slippery_score": round(avg_slippery, 2) if avg_slippery else None,
        "by_asset_type": [
            {
                "asset_type": r["asset_type"],
                "total": r["total"],
                "rated": r["rated"],
                "avg_rating": round(r["avg_rating"], 2) if r["avg_rating"] else None,
                "avg_slippery": round(r["avg_slippery"], 2),
            }
            for r in by_asset
        ],
        "top_variants": [
            {
                "variant_key": r["variant_key"],
                "asset_type": r["asset_type"],
                "avg_rating": round(r["avg_rating"], 2),
                "sample_size": r["n"],
            }
            for r in top_variants
        ],
        "bottom_variants": [
            {
                "variant_key": r["variant_key"],
                "asset_type": r["asset_type"],
                "avg_rating": round(r["avg_rating"], 2),
                "sample_size": r["n"],
            }
            for r in bottom_variants
        ],
        "recent_feedback": [
            {
                "generation_id": r["id"],
                "asset_type": r["asset_type"],
                "rating": r["rating"],
                "feedback": r["feedback"],
            }
            for r in recent
        ],
    }
