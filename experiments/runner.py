from __future__ import annotations
import argparse, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasks import build
from env import prompt, score

HOST = os.environ.get("DASHSCOPE_HOST", "https://ws-eafvwf0veluppvrv.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro", "qwen3.8-flash"]
CONDS = ["baseline", "overload", "overload_hap", "overload_gov"]


def call(model, messages, max_tokens):
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.0}
    req = urllib.request.Request(HOST.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=240) as r:
        b = json.loads(r.read().decode())
    return b["choices"][0]["message"].get("content") or "", time.time() - t0


def run(task, cond, model, out):
    if cond != "baseline":
        time.sleep(2.0)  # emulated queue/thermal latency
    msgs, cap = prompt(task, cond)
    try:
        content, dt = call(model, msgs, cap)
    except Exception as exc:
        content, dt = "", 0.0
    sc = score(task, content)
    rec = {"task_id": task["id"], "condition": cond, "model": model, "position": task["position"],
           **sc, "latency_s": round(dt, 2), "raw": content[:600]}
    with open(out, "a") as f: f.write(json.dumps(rec) + "\n")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results/overload.jsonl")
    ap.add_argument("--tasks", type=int, default=30); ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args(); os.makedirs(os.path.dirname(args.out), exist_ok=True); open(args.out, "w").close()
    tasks = build(args.tasks); jobs = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for model in MODELS:
            for cond in CONDS:
                for t in tasks:
                    jobs.append(pool.submit(run, t, cond, model, args.out))
        for i, f in enumerate(as_completed(jobs), 1):
            try: f.result()
            except Exception: pass
            if i % 30 == 0: print(f"{i}/{len(jobs)}", flush=True)
    print("done", len(jobs))


if __name__ == "__main__":
    main()
