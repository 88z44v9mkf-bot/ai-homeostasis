import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasks import build
from env import prompt, score
from runner import call
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro"]
LEVELS = [(0, 2500), (6, 2500), (0, 1200), (6, 1200)]

def run(task, delay, cap, model, out):
    if delay: time.sleep(delay)
    msgs, _ = prompt(task, "overload"); msgs[0]["content"] = msgs[0]["content"].replace("300", str(cap))
    try: content, dt = call(model, msgs, cap)
    except Exception: content, dt = "", 0.0
    rec = {"task_id": task["id"], "condition": "latency", "model": model, "delay_s": delay, "token_cap": cap,
           **score(task, content), "latency_s": round(dt, 2), "raw": content[:400]}
    open(out, "a").write(json.dumps(rec) + "\n")

if __name__ == "__main__":
    out = "results/latency.jsonl"; open(out, "w").close(); tasks = build(15); jobs = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for m in MODELS:
            for d, c in LEVELS:
                for t in tasks: jobs.append(pool.submit(run, t, d, c, m, out))
        for i, f in enumerate(as_completed(jobs), 1):
            try: f.result()
            except Exception: pass
    print("done", len(jobs))
