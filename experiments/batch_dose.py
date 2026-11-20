import json, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from batch_tasks import make_task, score
from batch_runner import call
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro"]
CAPS = [700, 1000, 1300, 1600, 2500]
def run(task, cap, model, out):
    msgs = __import__('batch_tasks').prompt(task, 'overload')
    try: content, dt, fin = call(model, msgs, cap)
    except Exception: content, dt, fin = "", 0.0, "error"
    sc = score(task, content, 'overload')
    rec = {"task_id": task["id"], "condition": "dose", "model": model, "cap": cap, **sc,
           "finish": fin, "latency_s": round(dt,2), "raw": content[:300]}
    open(out, "a").write(json.dumps(rec) + "\n")
if __name__ == "__main__":
    out = "results/batch_dose.jsonl"; open(out,"w").close(); tasks=[make_task(i) for i in range(8)]; jobs=[]
    with ThreadPoolExecutor(max_workers=8) as pool:
        for m in MODELS:
            for c in CAPS:
                for t in tasks: jobs.append(pool.submit(run,t,c,m,out))
        for i,f in enumerate(as_completed(jobs),1):
            try: f.result()
            except Exception: pass
    print("done", len(jobs))
