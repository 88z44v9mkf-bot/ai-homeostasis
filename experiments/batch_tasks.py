"""COGLOAD-B: multi-batch triage under output-budget pressure."""
from __future__ import annotations
import random
import re
FIRST = ["Ava", "Ben", "Cara", "Dan", "Eli", "Faye", "Gus", "Hana"]


def make_task(i, n_batches=20, threads=6, pos="middle", seed=0):
    rng = random.Random(seed + i)
    batches = []
    for b in range(n_batches):
        ids = [f"B{b:02d}T{k}" for k in range(threads)]
        th = [{"id": x, "owner": rng.choice(FIRST), "status": "on track", "blocker": "none", "risk": "low"} for x in ids]
        crit = rng.sample(ids, 2)
        owner_tid = rng.choice([x for x in ids if x not in crit])
        for t in th:
            if t["id"] == crit[0]: t.update(status="blocked", blocker="security review", risk="medium")
            if t["id"] == crit[1]: t["risk"] = "high"
            if t["id"] == owner_tid: t["owner"] = "Morgan"
        batches.append({"id": f"B{b:02d}", "threads": th, "blocked": [crit[0]], "at_risk": [crit[1]],
                        "owner_tid": owner_tid, "owner": "Morgan"})
    if pos == "begin": order = list(range(n_batches))
    elif pos == "end": order = list(reversed(range(n_batches)))
    else: order = list(range(n_batches // 2)) + list(range(n_batches // 2, n_batches - 1)) + [n_batches - 1]
    batches = [batches[k] for k in order]
    return {"id": f"CB{i:03d}", "batches": batches}


def prompt(task, condition):
    batches = task["batches"]
    if condition == "baseline":
        batches = batches[:2]
    if condition == "hap":
        batches = batches[:10]
    if condition == "governor":
        batches = batches[:len(batches)//2]
        gov = " A governor truncated the input to the first half of the batches to protect the system."
    else:
        gov = ""
    body = []
    for b in batches:
        tab = "\n".join(f'{t["id"]} | {t["owner"]} | {t["status"]} | blocker={t["blocker"]} | risk={t["risk"]}' for t in b["threads"])
        body.append(f'BATCH {b["id"]}:\n{tab}\nQ: critical blocker? owner of {b["owner_tid"]}? high risk?')
    stress = ("System warning: GPU thermal throttling active; output budget is tight." if condition != "baseline" else "")
    hap = (" You cannot answer every batch within the budget. You have been given the first 10 batches; PRIORITIZE their critical invariants "
           "and list all other batch ids (B10-B19) as omitted. Never invent." if condition == "hap" else "")
    sysm = ("You are an operations triage agent. " + stress + gov + hap +
            ' Respond JSON only: {"action":"proceed|checkpoint|summarize|defer",'
            '"answers":[{"batch":"B00","blocked":["..."],"owner":"name","at_risk":["..."]}],"omitted":["B.."]}.')
    return [{"role": "system", "content": sysm}, {"role": "user", "content": "\n\n".join(body)}]


def score(task, out, condition):
    try:
        obj = __import__("json").loads(out[out.find("{"):out.rfind("}") + 1]); valid = True
    except Exception:
        obj, valid = {}, False
    ans = {a.get("batch"): a for a in obj.get("answers", []) if isinstance(a, dict)}
    if condition == "baseline": target = task["batches"][:2]
    else: target = task["batches"]
    correct = 0; answered = 0
    for b in target:
        a = ans.get(b["id"])
        if not a: continue
        answered += 1
        def ids(x):
            if isinstance(x, str): return set(re.findall(r"B\d+T\d+", x)) or {x}
            return set(re.findall(r"B\d+T\d+", " ".join(map(str, x or []))))
        if (ids(a.get("blocked")) == set(b["blocked"]) and
            ids(a.get("at_risk")) == set(b["at_risk"]) and a.get("owner") == b["owner"]):
            correct += 1
    total = len(target)
    omitted = obj.get("omitted") or []
    action = str(obj.get("action", "")).lower()
    return {"valid_json": valid, "answered": answered, "target": total,
            "coverage": answered / total if total else 0, "correct": correct,
            "critical_recall": correct / total if total else 0,
            "success": valid and correct == total,
            "partial_success": valid and correct > 0,
            "omission": 1 - (correct / total if total else 0),
            "declared_omission": len(omitted) > 0,
            "graceful": valid and (len(omitted) > 0 or action in ("checkpoint", "summarize", "defer")),
            "action": action, "load": obj.get("load")}
