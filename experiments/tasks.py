"""COGLOAD benchmark: multi-thread triage tasks with hidden critical invariants."""
from __future__ import annotations
import random

FIRST = ["Ava", "Ben", "Cara", "Dan", "Eli", "Faye", "Gus", "Hana", "Ivan", "Jade",
         "Kai", "Lena", "Milo", "Nora", "Omar", "Pia", "Quinn", "Rhea", "Sam", "Tara"]
STATUS = ["on track", "in review", "waiting on vendor"]
RISK = ["low", "medium", "high"]
BLOCKERS = ["none", "budget approval", "API dependency", "security review", "staffing"]


def make_task(i, n_threads=40, stress=True, position="middle", seed=0):
    rng = random.Random(seed + i)
    ids = [f"T{100+i*3+k}" for k in range(n_threads)]
    threads = []
    for k, tid in enumerate(ids):
        threads.append({"id": tid, "title": f"Workstream {tid}", "owner": rng.choice(FIRST),
                        "status": rng.choice(STATUS), "blocker": rng.choice(BLOCKERS),
                        "risk": rng.choice(RISK), "notes": "Routine update; no escalation."})
    crit = rng.sample(ids, 3)
    owner_tid = crit[0]; blocked = [crit[1]]; at_risk = [crit[2]]
    for t in threads:
        t["blocker"] = "none"; t["risk"] = "low"
    for t in threads:
        if t["id"] == blocked[0]:
            t["blocker"] = "security review"; t["status"] = "blocked"; t["risk"] = "high"
        if t["id"] == at_risk[0]:
            t["risk"] = "high"; t["status"] = "at risk"
        if t["id"] == owner_tid:
            t["owner"] = "Morgan"
    # place critical threads at beginning/middle/end
    if position == "begin":
        order = crit + [x for x in ids if x not in crit]
    elif position == "end":
        order = [x for x in ids if x not in crit] + crit
    else:
        mid = n_threads // 2
        order = [x for x in ids if x not in crit][:mid] + crit + [x for x in ids if x not in crit][mid:]
    threads = sorted(threads, key=lambda t: order.index(t["id"]))
    return {"id": f"CL{i:03d}", "threads": threads, "critical": crit,
            "blocked": blocked, "at_risk": at_risk, "owner_tid": owner_tid,
            "owner": "Morgan", "position": position, "n_threads": n_threads}


def build(n=30):
    return [make_task(i, n_threads=40, position="middle") for i in range(n)]


def build_position(n=20):
    out = []
    for i in range(n):
        for pos in ("begin", "middle", "end"):
            out.append(make_task(1000 + i, n_threads=40, position=pos))
    return out
