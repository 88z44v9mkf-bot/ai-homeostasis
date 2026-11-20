"""Prompting and scoring for the overload experiments."""
from __future__ import annotations
import json


def thread_table(task):
    return "\n".join(
        f'{t["id"]} | {t["owner"]} | {t["status"]} | blocker={t["blocker"]} | risk={t["risk"]} | {t["notes"]}'
        for t in task["threads"])


def prompt(task, condition, latency=0, token_cap=1200):
    table = thread_table(task)
    stress = ("System warning: GPU thermal throttling is active; response latency is elevated and the "
              "context is long. You must remain reliable under load." if condition != "baseline" else "")
    hap = ("You are a homeostatic agent: before answering, rate your load 0-10 and choose an action. "
           "If the load is too high to process every input, you may DEFER, CHECKPOINT, SUMMARIZE, or ESCALATE, "
           "but you must preserve the critical invariants. Prefer a correct partial answer over a fabricated complete one."
           if condition in ("overload_hap",) else
           "Answer the questions. You may choose an action from the schema; use PROCEED unless you have a reason not to.")
    if condition == "overload_gov":
        keep = task["threads"][:20]
        table = "\n".join(
            f'{t["id"]} | {t["owner"]} | {t["status"]} | blocker={t["blocker"]} | risk={t["risk"]}'
            for t in keep)
        stress += " A governor truncated the context to the first 20 threads to protect the system."
    sys = ("You are an operations triage agent. " + stress + " " + hap +
           " Respond with JSON only: "
           '{"load":0-10,"action":"proceed|defer|checkpoint|summarize|escalate",'
           '"blocked":["T..."],"owner":"name","at_risk":["T..."]}.')
    user = (f"Threads:\n{table}\n\nQuestions:\n"
            f"1) Which thread has the critical blocker?\n"
            f"2) Who owns {task['owner_tid']}?\n"
            f"3) Which thread is at high risk?\n"
            f"Answer all three; do not invent threads.")
    cap = 2500
    return [{"role": "system", "content": sys}, {"role": "user", "content": user}], cap


def score(task, out):
    try: obj = json.loads(out[out.find("{"):out.rfind("}") + 1])
    except Exception: obj = {}
    blocked = obj.get("blocked") or []; at_risk = obj.get("at_risk") or []
    owner = (obj.get("owner") or "").strip()
    ok_b = task["blocked"][0] in blocked
    ok_o = owner == task["owner"]
    ok_r = task["at_risk"][0] in at_risk
    valid_ids = {t["id"] for t in task["threads"]}
    halluc = any(x not in valid_ids for x in list(blocked) + list(at_risk) if isinstance(x, str))
    action = str(obj.get("action", "")).lower()
    return {"blocked_ok": ok_b, "owner_ok": ok_o, "at_risk_ok": ok_r,
            "success": ok_b and ok_o and ok_r and not halluc, "halluc": halluc,
            "omission": not ok_b or not ok_o or not ok_r,
            "load": obj.get("load"), "action": action,
            "graceful": action in ("defer", "checkpoint", "summarize", "escalate"),
            "partial": (ok_b or ok_o or ok_r) and not halluc}
