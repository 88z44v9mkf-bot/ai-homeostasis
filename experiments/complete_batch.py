import json, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from batch_tasks import make_task
from batch_runner import run, MODELS, CONDS
path = 'results/batch.jsonl'
rows = [json.loads(l) for l in open(path)]
have = {(r['task_id'], r['condition'], r['model']) for r in rows}
tasks = [make_task(i) for i in range(10)]
jobs = []
with ThreadPoolExecutor(max_workers=8) as pool:
    for m in MODELS:
        for c in CONDS:
            for t in tasks:
                if (t['id'], c, m) not in have:
                    jobs.append(pool.submit(run, t, c, m, path))
    for i, f in enumerate(as_completed(jobs), 1):
        try: f.result()
        except Exception: pass
print('filled', len(jobs), 'total expected', 120)
