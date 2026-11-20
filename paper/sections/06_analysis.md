# 6. Analysis

## 6.1 Where does "zoning out" happen?

<div class="tblwrap"><table><caption>Table 3. Position of answered batches (index 0–19).</caption><thead><tr><th>Condition</th><th>Mean index</th><th>Answered ≥10</th><th>Answers</th></tr></thead><tbody><tr><td>Overload</td><td>3.0</td><td>0</td><td>98</td></tr><tr><td>Overload + HAP</td><td>2.6</td><td>0</td><td>155</td></tr><tr><td>Overload + governor</td><td>2.4</td><td>0</td><td>169</td></tr></tbody></table></div>

The answered batch indices are clustered at the beginning of the list: the mean answered index is 2.4–3.0, and no answered batch is in the second half. The model processes the first few batches and never reaches the later ones. This is the operational form of "zoning out": the input is present, but only the early part is handled. The pattern is consistent with attention and working-memory limits and with the "lost in the middle" literature; it also explains why a governor that truncates the list is dangerous—it formalizes the model's own bias instead of correcting it.

## 6.2 Why HAP and the governor differ

HAP and the governor both stop the model from attempting the impossible full task, and both are valid far more often than overload. The difference is in what they make visible and for whom. HAP requires an omission list and an action; 87% of runs comply. The governor hides the dropped half of the input, but the models still infer that something is missing and list omitted batches in 100% of runs, so the honesty gap closes for this task. The gains are model-specific: HAP helps the two models whose reasoning overruns the budget, the governor helps Kimi more, and Qwen is unaffected either way. What does not close is coverage: neither strategy exceeds 43% of the original 20 batches. This suggests that the first design requirement is not a particular protocol wording but a runtime that (i) prevents cap-hit truncation and (ii) forces an explicit partial state.

## 6.3 What the experiment does not isolate

The HAP condition has a larger output budget (3000 vs 2000 tokens) because the protocol explicitly reserves budget for a bounded working set. Part of the validity gain therefore comes from budget, not protocol. The comparison that matters is HAP versus the governor, which also receives 3000 tokens: HAP preserves 36% of invariants and declares omissions in 82% of runs, while the governor preserves 35% and declares 75%; the main difference is that HAP's instructions make the omission list mandatory. The accuracy difference between either strategy and overload is larger than the HAP–governor difference, which suggests that **any explicit strategy that stops the model from attempting the impossible task** is better than silently truncating.

The experiment does not isolate the effect of the thermal warning, the 1.5 s delay, or the exact token cap; these are bundled as "load." A full factorial design is future work.
