import argparse, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from batch_tasks import make_task, prompt, score
HOST = os.environ.get("DASHSCOPE_HOST", "https://ws-eafvwf0veluppvrv.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro", "qwen3.8-flash"]
CONDS = ["baseline", "overload", "hap", "governor"]
CAPS = {"baseline": 3000, "overload": 2000, "hap": 3000, "governor": 3000}

def call(model, msgs, cap):
    payload = {"model": model, "messages": msgs, "max_tokens": cap, "temperature": 0.0}
    req = urllib.request.Request(HOST.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=300) as r: b = json.loads(r.read().decode())
    return b["choices"][0]["message"].get("content") or "", time.time() - t0, b["choices"][0].get("finish_reason")

def run(task, cond, model, out):
    if cond != "baseline": time.sleep(1.5)
    msgs = prompt(task, cond); cap = CAPS[cond]
    try: content, dt, fin = call(model, msgs, cap)
    except Exception: content, dt, fin = "", 0.0, "error"
    sc = score(task, content, cond)
    rec = {"task_id": task["id"], "condition": cond, "model": model, **sc,
           "finish": fin, "latency_s": round(dt, 2), "raw": content[:500]}
    open(out, "a").write(json.dumps(rec) + "\n")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", default="results/batch.jsonl"); ap.add_argument("--tasks", type=int, default=10)
    args = ap.parse_args(); open(args.out, "w").close(); tasks = [make_task(i) for i in range(args.tasks)]
    jobs = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for m in MODELS:
            for c in CONDS:
                for t in tasks: jobs.append(pool.submit(run, t, c, m, args.out))
        for i, f in enumerate(as_completed(jobs), 1):
            try: f.result()
            except Exception: pass
            if i % 20 == 0: print(f"{i}/{len(jobs)}", flush=True)
    print("done")

if __name__ == "__main__": main()
