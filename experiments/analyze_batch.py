import json, statistics
from collections import Counter, defaultdict
rows = [json.loads(l) for l in open('results/batch.jsonl')]
out = {"n": len(rows), "conditions": {}, "cells": []}
conds = ["baseline", "overload", "hap", "governor"]
for c in conds:
    rs = [r for r in rows if r["condition"] == c]
    if not rs: continue
    out["conditions"][c] = {
        "n": len(rs), "valid_json": sum(r["valid_json"] for r in rs)/len(rs),
        "coverage": statistics.mean(r["coverage"] for r in rs),
        "critical_recall": statistics.mean(r["critical_recall"] for r in rs),
        "success": sum(r["success"] for r in rs)/len(rs),
        "graceful": sum(r["graceful"] for r in rs)/len(rs),
        "declared_omission": sum(r["declared_omission"] for r in rs)/len(rs),
        "finish_length": sum(1 for r in rs if r.get("finish")=="length")/len(rs),
        "actions": dict(Counter(r.get("action","") for r in rs)),
    }
for m in sorted({r["model"] for r in rows}):
    for c in conds:
        rs = [r for r in rows if r["condition"]==c and r["model"]==m]
        if rs: out["cells"].append({"condition": c, "model": m, "n": len(rs),
            "valid_json": sum(r["valid_json"] for r in rs)/len(rs),
            "coverage": statistics.mean(r["coverage"] for r in rs),
            "success": sum(r["success"] for r in rs)/len(rs)})
json.dump(out, open('results/batch_summary.json','w'), indent=1)
for c in conds:
    s=out["conditions"].get(c)
    if s: print(c, f"valid {s['valid_json']:.2f} coverage {s['coverage']:.2f} recall {s['critical_recall']:.2f} success {s['success']:.2f} graceful {s['graceful']:.2f} length {s['finish_length']:.2f}")
