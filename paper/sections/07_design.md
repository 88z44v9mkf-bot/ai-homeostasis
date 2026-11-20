# 7. Designing for soft failure

The experiments suggest that the goal is not to prevent all degradation—under enough load, every system degrades—but to make degradation visible, bounded, and recoverable. We derive six design rules.

## 7.1 Load telemetry

The runtime should expose a small, typed load signal: context size, queue depth, p95 latency, token budget used, retry count, and thermal state where available. The model should see a compact version of this signal. HAP's `load` field is the model's own estimate; the runtime's telemetry is the ground truth against which it is calibrated.

## 7.2 Explicit degradation actions

An agent should be able to say "I cannot do this now" without being punished for it when true. The action set should include at least `defer`, `checkpoint`, `summarize`, and `escalate`, and the runtime must honor the choice. A deferred task must not be marked complete.

## 7.3 Invariant preservation

Degradation is safe only if critical invariants survive. HAP requires the agent to name the invariants before it summarizes or narrows scope. In COGLOAD the invariants are the three critical threads; in production they are safety constraints, payment limits, or legal obligations. The protocol is general: name them, preserve them, verify them.

## 7.4 Content-aware protection

The governor experiment is a warning. Truncating context by position is cheap and can protect the runtime, but it can also delete the one thread that mattered. Engineering protection must be content-aware: retrieve by relevance, preserve pinned invariants, and mark what was dropped so the model can report a partial view instead of assuming completeness.

## 7.5 Checkpoint and resume

A long task should write a compact checkpoint (goal, invariants, completed steps, open questions, evidence ids) before it degrades. Recovery then means reloading the checkpoint and resuming, not re-running from zero. This is the machine analogue of stepping away from the window and coming back.

## 7.6 Calibration and honest reporting

The model's load report should be treated as a signal to be calibrated, not as ground truth. The runtime can learn a mapping from telemetry and self-report to actual failure risk, and can force a checkpoint when the two disagree. Honest partial answers should be rewarded; fabricated completeness should be penalized.

## 7.7 A reference runtime

A practical implementation is a wrapper with four layers: (i) telemetry, (ii) a HAP tool schema, (iii) a governor that can defer or checkpoint, and (iv) an evidence log. The wrapper does not need to know the model's internals; it only needs to observe the contract. This makes HAP portable across model families and deployment environments (cloud, on-premise, cockpit, edge).
