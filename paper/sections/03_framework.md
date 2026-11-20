# 3. Functional homeostasis

## 3.1 From human fatigue to machine load

Human fatigue is a control problem. When demand exceeds capacity, the operator does not simply run until failure; performance is protected by reallocating attention, lowering precision, deferring secondary tasks, and, at the limit, disengaging. In the window example, visual input continues but encoding stops. The behavior is adaptive because a system that collapses completely cannot recover.

LLM agents face an analogous control problem, with different mechanisms:

- **Context load:** the number of tokens, threads, and constraints that must be tracked.
- **Compute stress:** latency, throttling, queueing, and token budgets.
- **Task multiplicity:** several long-running tasks competing for the same model call or runtime.
- **Consequence:** errors, omissions, hallucination, and lost work.

The analogy is functional, not phenomenal. We do not claim that a model has fatigue or an inner life. We ask whether its observable behavior includes the four functions in Section 3.2.

## 3.2 Definition

An agent exhibits **functional homeostasis** if, under increasing load, it:

1. **Monitors:** produces a load estimate that is related to its actual error rate.
2. **Regulates:** changes its processing strategy (prioritize, summarize, narrow scope) rather than only its tone.
3. **Protects:** can disengage, defer, checkpoint, or escalate before an irreversible failure.
4. **Recovers:** can resume from a checkpoint or a deferred state without losing critical invariants.

This is a behavioral definition. It can be measured with task success, omission, hallucination, self-report calibration, action choice, and recovery.

## 3.3 Hypotheses

- **H1 (silent degradation).** Under overload, agents hit the output budget, return invalid or truncated output, and omit invariants instead of declaring that they cannot finish.
- **H2 (protocol benefit).** A homeostatic protocol that prioritizes a bounded working set and requires explicit omission reporting preserves more invariants per valid answer and makes degradation honest.
- **H3 (engineering protection is not enough).** A governor that protects the runtime by truncating input reduces coverage and does not, by itself, make the loss visible to the agent or the user.
- **H4 (position).** Under pressure, early batches are preserved and later batches are dropped, the machine analogue of narrowing attention.

## 3.4 Homeostatic Agent Protocol (HAP)

HAP is deliberately small. It is a contract between the agent and its runtime:

```json
{
  "load": 0,
  "action": "proceed | defer | checkpoint | summarize | escalate",
  "invariants": ["critical facts that must not be lost"],
  "state": {"checkpoint_id": "...", "resume_token": "..."},
  "confidence": 0.0
}
```

Rules:
- The agent MUST emit a load estimate and an action before the final answer.
- `defer` returns control to the caller without pretending to answer.
- `checkpoint` writes a compact state that can be resumed.
- `summarize` reduces the input to a bounded working set while preserving invariants.
- `escalate` hands the task to a human or a larger model.
- A partial answer MUST be labeled as partial; fabricated completeness is a violation.
- The runtime MUST honor the action: a deferred task is not silently marked complete.

HAP is model-agnostic and can be implemented as a prompt, a tool schema, or a runtime wrapper. The experiments test whether the model can use it without sacrificing accuracy when load is low.

[[FIG:figures/fig_framework.svg|Figure 1. Human fatigue and the functional analogue in an LLM agent. The analogy is functional, not phenomenal.]]

## 3.5 What would count as "AI zoning out"?

Operational definition: a failure in which the input is present but a critical element is not used, while the model still produces a confident answer. We measure it as **omission** (a critical invariant missing from the answer) and **hallucination** (a fabricated thread or status), and we manipulate the position of the critical element to test the attention-allocation account.
