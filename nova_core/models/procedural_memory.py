from __future__ import annotations
"""ProceduralMemory — rule table mapping (context ➟ goal) to callable action.

A *rule* is a tuple:
   (name: str,
    condition_fn: Callable[[dict], bool],   # evaluates WM / SM snapshot
    goal: str,
    action_fn: Callable[[dict], None])      # side‑effect or intent enqueue

`evaluate(context)` iterates all rules, fires those whose conditions return True.
Returned list contains (goal, action_fn) pairs so an *ActionExecutor* can pick.
"""
from typing import Callable, List, Tuple

Rule = Tuple[str, Callable[[dict], bool], str, Callable[[dict], None]]

__all__ = ["ProceduralMemory", "Rule"]


class ProceduralMemory:
    """Very small forward‑chaining rule engine."""

    def __init__(self):
        self._rules: List[Rule] = []

        self.add_rule(
            name="ping_pong",
            condition_fn=lambda ctx: (
                isinstance(ctx.get("payload"), dict)
                and "message" in ctx["payload"]
                and "ping" in ctx["payload"]["message"].lower()
            ),
            goal="pong",
            action_fn=lambda ctx: print("[Action] pong")
        )


    # ‑‑‑ rule management ‑‑‑ -------------------------------------------------
    def add_rule(self, name: str, condition_fn: Callable[[dict], bool], goal: str,
                 action_fn: Callable[[dict], None]):
        self._rules.append((name, condition_fn, goal, action_fn))

    def remove_rule(self, name: str):
        self._rules = [r for r in self._rules if r[0] != name]

    # ‑‑‑ evaluation ‑‑‑ -------------------------------------------------------
    def evaluate(self, context: dict) -> List[Tuple[str, Callable[[dict], None]]]:
        """Return actions whose conditions hold in the given context."""
        ready: List[Tuple[str, Callable[[dict], None]]] = []
        for name, cond, goal, action in self._rules:
            try:
                if cond(context):
                    ready.append((goal, action))
            except Exception as exc:
                # In production you might log & disable the faulty rule
                print(f"[ProceduralMemory] rule '{name}' error: {exc}")
        return ready

    # ‑‑‑ convenience -----------------------------------------------------------------
    def __len__(self):
        return len(self._rules)

    def __iter__(self):
        return iter(self._rules)


# ‑‑‑ example usage -------------------------------------------------------------------
if __name__ == "__main__":
    pm = ProceduralMemory()

    # Rule: if it's after 18:00, suggest shutting down heavy compute jobs.
    pm.add_rule(
        "evening_power_save",
        lambda ctx: ctx.get("hour", 24) >= 18 and ctx.get("system", {}).get("cpu%", 0) < 30,
        "reduce_load",
        lambda ctx: print("[Action] Lowering GPU training workload")
    )

    ctx = {"hour": 19, "system": {"cpu%": 25}}
    for goal, action in pm.evaluate(ctx):
        print("Goal:", goal)
        action(ctx)
