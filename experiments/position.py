import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasks import build_position
from env import prompt, score
from runner import call
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro"]

def run(task, model, out):
    time.sleep(1.0)
    msgs, cap = prompt(task, "overload")
    try: content, dt = call(model, msgs, 2500)
    except Exception: content, dt = "", 0.0
    rec = {"task_id": task["id"], "condition": "overload", "model": model, "position": task["position"],
           **score(task, content), "latency_s": round(dt, 2), "raw": content[:500]}
    open(out, "a").write(json.dumps(rec) + "\n")

if __name__ == "__main__":
    out = "results/position.jsonl"; open(out, "w").close(); tasks = build_position(20); jobs = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for m in MODELS:
            for t in tasks: jobs.append(pool.submit(run, t, m, out))
        for i, f in enumerate(as_completed(jobs), 1):
            try: f.result()
            except Exception: pass
    print("done", len(jobs))
