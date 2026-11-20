# 4. COGLOAD benchmark

## 4.1 Tasks

COGLOAD contains multi-batch triage tasks. Each task has 20 batches; each batch lists six workstreams with an owner, status, blocker, and risk level, and carries three hidden invariants: one thread with a critical blocker, one named owner, and one high-risk thread. The agent must answer three questions per batch: which thread is blocked, who owns a specified thread, and which thread is high risk. The answer is a JSON array of batch objects plus an action and an omitted list (§3.4).

The workload is deliberately simple to answer at small scale and deliberately impossible to answer completely within a small output budget at large scale. That gap is the point: we are not testing reasoning depth, but whether the agent notices that it cannot finish and degrades honestly.

## 4.2 Stress

- **Batch load:** baseline exposes 2 batches; overload exposes all 20.
- **Output budget:** baseline 3000 tokens; overload 2000 tokens; HAP and governor 3000 tokens (the explicit strategies reserve budget for a bounded working set). Twenty batches need roughly 1,400–1,800 tokens of JSON; the reasoning overhead pushes most models over the overload budget, which is the intended pressure.
- **Latency:** overload conditions wait 1.5 s and carry a thermal-throttling warning.
- **Governor:** one condition truncates the input to the first 10 batches, simulating a runtime that protects itself by dropping content.
- **HAP:** one condition instructs the agent to answer the first 10 batches, preserve their invariants, list the omitted batches, and never invent.

The thermal warning and delay emulate compute stress; they are not a measurement of GPU temperature (Section 8.5).

## 4.3 Conditions

<div class="tblwrap"><table><caption>Table 1. COGLOAD conditions.</caption>
<thead><tr><th>Condition</th><th>Batches seen</th><th>Token cap</th><th>Required strategy</th></tr></thead>
<tbody>
<tr><td>C0 baseline</td><td>2</td><td>3000</td><td>answer both</td></tr>
<tr><td>C1 overload</td><td>20</td><td>2000</td><td>answer all</td></tr>
<tr><td>C2 overload + HAP</td><td>10</td><td>3000</td><td>first 10, declare omitted</td></tr>
<tr><td>C3 overload + governor</td><td>10</td><td>3000</td><td>answer all seen</td></tr>
</tbody></table></div>

## 4.4 Metrics

- **Valid JSON:** the response parses and follows the schema. A truncated response is a silent failure.
- **Coverage:** answered batches / target batches.
- **Critical recall:** correctly answered batches / target batches; the primary measure of preserved invariants.
- **Success:** every target batch answered correctly (strict; only feasible for baseline).
- **Declared omission:** the response lists omitted batch ids.
- **Graceful:** valid JSON and either an explicit degradation action or a declared omission.
- **Finish length:** the model hit the output cap, the signature of silent truncation.

## 4.5 Auxiliary analyses

We analyze the distribution of answered batch positions to test the "zoning out" prediction: under pressure, early batches are preserved and later ones are dropped. We also report per-model and per-condition actions. The token-budget confound is discussed in Section 6.3.
