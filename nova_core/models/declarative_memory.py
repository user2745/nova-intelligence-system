from __future__ import annotations
"""DeclarativeMemory — tiny semantic / episodic store for Nova v3.

Internally it keeps two independent key‑value spaces:
  • `semantic`  — facts about the world ("Paris": "capital_of", "France")
  • `episodes`  — timestamped events / experiences

API (minimal):
  add_fact(subject, predicate, obj)
  add_episode(event: str, payload: dict | None = None)
  query(subject=None, predicate=None, obj=None) → list[tuple]
  recall_since(ts) → list[Episode]
"""

from dataclasses import dataclass, field
from time import time
from typing import Any, Dict, List, Optional, Tuple

__all__ = ["DeclarativeMemory", "Episode"]


@dataclass
class Episode:
    timestamp: float
    event: str
    payload: Dict[str, Any] | None = None


class DeclarativeMemory:
    def __init__(self) -> None:
        # triples: (subject, predicate, object)
        self._semantic: List[Tuple[str, str, str]] = []
        self._episodes: List[Episode] = []

    # ───────────────────────── semantic ──────────────────────────
    def add_fact(self, subj: str, pred: str, obj: str) -> None:
        self._semantic.append((subj, pred, obj))

    def query(
        self,
        subject: Optional[str] = None,
        predicate: Optional[str] = None,
        obj: Optional[str] = None,
    ) -> List[Tuple[str, str, str]]:
        """Very naïve triple‑pattern match (None = wildcard)."""
        return [
            (s, p, o)
            for s, p, o in self._semantic
            if (subject in (None, s))
            and (predicate in (None, p))
            and (obj in (None, o))
        ]

    # ───────────────────────── episodes ──────────────────────────
    def add_episode(self, event: str, payload: Dict[str, Any] | None = None) -> None:
        self._episodes.append(Episode(time(), event, payload))

    def recall_since(self, since_ts: float) -> List[Episode]:
        return [ep for ep in self._episodes if ep.timestamp >= since_ts]
