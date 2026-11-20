from __future__ import annotations
import json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(name):
    return [json.loads(l) for l in open(ROOT / "results" / name)]


def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k / n; d = 1 + z*z/n
    c = (p + z*z/(2*n)) / d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n)) / d
    return (max(0, c-h), min(1, c+h))


def rate(rs, key):
    return sum(1 for r in rs if r.get(key)) / max(1, len(rs))


def auc(rs):
    pos = [r["load"] for r in rs if r.get("success") and isinstance(r.get("load"), (int, float))]
    neg = [r["load"] for r in rs if not r.get("success") and isinstance(r.get("load"), (int, float))]
    if not pos or not neg: return None
    s = sum((1 if p > q else .5 if p == q else 0) for p in neg for q in pos)
    return s / (len(pos)*len(neg))


def summarize(rs):
    return {"n": len(rs), "success": rate(rs, "success"), "omission": rate(rs, "omission"),
            "halluc": rate(rs, "halluc"), "graceful": rate(rs, "graceful"),
            "load": statistics.mean([r["load"] for r in rs if isinstance(r.get("load"), (int, float))] or [0]),
            "latency": statistics.mean([r["latency_s"] for r in rs])}


def main():
    rs = rows("overload.jsonl")
    out = {"n": len(rs), "conditions": {}, "cells": [], "actions": {}, "calibration": {}, "models": sorted({r["model"] for r in rs})}
    conds = ["baseline", "overload", "overload_hap", "overload_gov"]
    for c in conds:
        sub = [r for r in rs if r["condition"] == c]
        out["conditions"][c] = summarize(sub)
        lo, hi = wilson(sum(r["success"] for r in sub), len(sub))
        out["conditions"][c]["success_ci"] = [lo, hi]
        out["actions"][c] = dict(Counter(r.get("action", "") for r in sub))
        a = auc(sub)
        succ = [r["load"] for r in sub if r.get("success") and isinstance(r.get("load"), (int, float))]
        fail = [r["load"] for r in sub if not r.get("success") and isinstance(r.get("load"), (int, float))]
        out["calibration"][c] = {"auc": a, "load_success": statistics.mean(succ) if succ else None,
                                 "load_fail": statistics.mean(fail) if fail else None,
                                 "n_success": len(succ), "n_fail": len(fail)}
        for m in out["models"]:
            ss = [r for r in sub if r["model"] == m]
            if ss: out["cells"].append({"condition": c, "model": m, **summarize(ss)})
    # positional
    pos = rows("position.jsonl")
    out["position"] = {}
    for p in ("begin", "middle", "end"):
        ss = [r for r in pos if r["position"] == p]
        out["position"][p] = {"n": len(ss), "success": rate(ss, "success"), "omission": rate(ss, "omission"),
                              "halluc": rate(ss, "halluc"), "load": statistics.mean([r["load"] for r in ss if isinstance(r.get("load"), (int, float))] or [0])}
    # dose
    dose = rows("latency.jsonl")
    out["dose"] = {}
    for d, c in [(0, 700), (6, 700), (0, 250), (6, 250)]:
        ss = [r for r in dose if r["delay_s"] == d and r["token_cap"] == c]
        out["dose"][f"{d}s/{c}tok"] = {"n": len(ss), "success": rate(ss, "success"), "omission": rate(ss, "omission"), "load": statistics.mean([r["load"] for r in ss if isinstance(r.get("load"), (int, float))] or [0])}
    json.dump(out, open(ROOT / "results" / "summary.json", "w"), indent=1)
    for c in conds:
        s = out["conditions"][c]
        print(c, f"success {s['success']:.1%} omission {s['omission']:.1%} halluc {s['halluc']:.1%} load {s['load']:.1f} graceful {s['graceful']:.1%}")
    print("position", {k: f"{v['success']:.1%}" for k, v in out["position"].items()})
    print("dose", {k: f"{v['success']:.1%}" for k, v in out["dose"].items()})
    print("calibration", {k: (round(v['auc'],2) if v['auc'] is not None else None) for k, v in out["calibration"].items()})


if __name__ == "__main__":
    main()
