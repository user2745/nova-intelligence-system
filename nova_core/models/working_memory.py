from __future__ import annotations
"""WorkingMemory — fast, volatile scratch‑pad for the current cognitive cycle.

✅ Dict‑like API (get / set / del / in)
✅ Automatic TTL eviction (seconds)
✅ Explicit `next_cycle()` wipe to synchronise with Nova’s 50 ms tick
"""
from collections import UserDict
from time import monotonic
from typing import Any, Dict, Iterator, Tuple

__all__ = ["WorkingMemory"]


class WorkingMemory(UserDict):
    """Key–value store with per‑item TTL and per‑cycle flushing.

    Example
    -------
    >>> wm = WorkingMemory()
    >>> wm.set("cpu", 12.3, ttl=0.2)
    >>> "cpu" in wm
    True
    >>> time.sleep(0.3)
    >>> "cpu" in wm
    False
    """

    def __init__(self) -> None:
        super().__init__()
        self._exp: Dict[str, float] = {}  # key → expiry wall‑clock (monotonic)
        self.cycle_count: int = 0

    # ────────────────────────── core dict API ──────────────────────────
    def __getitem__(self, key: str) -> Any:  # type: ignore[override]
        if key in self and not self._is_expired(key):
            return super().__getitem__(key)
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        return super().__contains__(key) and not self._is_expired(key)  # type: ignore[arg-type]

    # ─────────────────────────── custom helpers ────────────────────────
    def set(self, key: str, value: Any, *, ttl: float | None = None) -> None:
        """Insert *key* with optional time‑to‑live in seconds."""
        super().__setitem__(key, value)
        if ttl is not None:
            self._exp[key] = monotonic() + ttl
        elif key in self._exp:
            del self._exp[key]

    def get_ttl(self, key: str) -> float | None:
        """Seconds until expiry, or *None* if no TTL/doesn’t exist."""
        if key not in self or key not in self._exp:
            return None
        return max(0.0, self._exp[key] - monotonic())

    def next_cycle(self) -> None:
        """Flush entire store — called once every 50 ms tick if desired."""
        self.data.clear()
        self._exp.clear()
        self.cycle_count += 1

    # ─────────────────────────── internals ────────────────────────────
    def _is_expired(self, key: str) -> bool:
        exp = self._exp.get(key)
        if exp is None:
            return False
        if monotonic() >= exp:
            # auto‑purge
            super().__delitem__(key)
            del self._exp[key]
            return True
        return False

    # keep iterator sane (skip dead keys)
    def items(self) -> Iterator[Tuple[str, Any]]:  # type: ignore[override]
        for k in list(self.data.keys()):
            if not self._is_expired(k):
                yield k, self.data[k]
