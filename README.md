# Do AI Systems Zone Out? Functional Homeostasis and Graceful Degradation in LLM Agents under Cognitive Load

Jipu Su — Geely Automobile Group, Hangzhou, China.

This repository contains COGLOAD-B, the HAP protocol, the raw LLM trajectories, the paper, and the analysis.

## Question

A tired person staring out of a window is not processing the scene. The eyes are open, but the input is not handled. Do LLM agents exhibit a functional analogue under load?

## Benchmark

COGLOAD-B: 10 multi-batch triage tasks, 20 batches each, six threads per batch, three hidden invariants per batch. Conditions: baseline (2 batches, 3000 tokens), overload (20 batches, 2000 tokens), HAP (first 10 batches, 3000 tokens, explicit omission), governor (first 10 batches, 3000 tokens, content-blind truncation).

Models: deepseek-v4.1-flash-1017, kimi-k3.1-pro, qwen3.8-flash. 120 trajectories at temperature 0.

## Results

| Condition | Valid JSON | Coverage | Critical recall | Declared omission | Hit cap |
|---|---|---|---|---|---|
| Baseline | 100% | 100% | 97% | 0% | 0% |
| Overload | 37% | 37% | 37% | 0% | 63% |
| Overload + HAP | 87% | 43% | 40% | 87% | 13% |
| Overload + governor | 100% | 37% | 35% | 100% | 0% |

The collapse is model-specific: DeepSeek and Kimi truncate; Qwen-Flash answers all batches at 2000 tokens. The answered batches are always at the beginning of the list (mean index 2.4–3.0 of 20; none in the second half): a functional "zoning out".

## Files

```
experiments/batch_tasks.py   COGLOAD-B tasks, prompts, scorer
experiments/batch_runner.py  model runner
experiments/analyze_batch.py analysis
results/batch.jsonl          raw trajectories
results/batch_summary.json   aggregates
paper/main.pdf               paper (12 pages)
paper/sections/              Markdown sources
```

## Reproduce

```bash
export DASHSCOPE_API_KEY=...
python3 experiments/batch_runner.py --out results/batch.jsonl --tasks 10
python3 experiments/analyze_batch.py
python3 paper/build/build.py
```

## License

Code MIT; paper and results CC BY 4.0.
