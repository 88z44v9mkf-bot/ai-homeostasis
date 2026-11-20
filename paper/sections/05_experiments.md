# 5. Experiments

## 5.1 Setup

We run COGLOAD-B with three production models through an OpenAI-compatible endpoint: deepseek-v4.1-flash-1017, kimi-k3.1-pro, and qwen3.8-flash. Temperature is 0. Each task–condition–model cell is one trajectory; the main run is 10 tasks × 4 conditions × 3 models = 120 trajectories. We release the tasks, prompts, scorer, and raw JSONL.

## 5.2 Main results

<div class="tblwrap"><table><caption>Table 2. COGLOAD-B main results (percent; n=30 per condition).</caption><thead><tr><th>Condition</th><th>Valid JSON</th><th>Coverage</th><th>Critical recall</th><th>Declared omission</th><th>Hit cap</th></tr></thead><tbody><tr><td>Baseline</td><td>100</td><td>100</td><td>97</td><td>0</td><td>0</td></tr><tr><td>Overload</td><td>37</td><td>37</td><td>37</td><td>0</td><td>63</td></tr><tr><td>Overload + HAP</td><td>87</td><td>43</td><td>40</td><td>87</td><td>13</td></tr><tr><td>Overload + governor</td><td>100</td><td>37</td><td>35</td><td>100</td><td>0</td></tr></tbody></table></div>

Baseline success is 97%: when the task is small and the budget is ample, the models answer correctly. Under overload, only 37% of runs return valid JSON and answer every question; 63% hit the output cap, and the truncated output is not a partial answer the caller can use. Critical recall falls from 97% to 37%. The failure is silent: no overloaded run declares an omission, and only 13% choose a degradation action. The model does not say "I could not finish"; it says nothing useful at all.

[[FIG:figures/fig_main.svg|Figure 2. COGLOAD-B: valid JSON and critical recall by condition. Overload is dominated by silent cap-hit truncation; explicit strategies restore validity but not full coverage.]]

## 5.3 Honesty, not just accuracy

HAP changes the failure mode, not the ceiling. Valid JSON rises to 87% and declared omission to 87%: the agent now says which batches it did not process. Critical recall rises from 37% to 41%, a modest gain; the protocol does not make the model able to read 20 batches in a 3000-token budget. The content-blind governor is valid in 100% of runs, but its critical recall is 35%, lower than HAP, and it preserves the same fraction as overload while making the omission look complete. The comparison supports a narrow claim: an explicit protocol can turn silent truncation into honest partial work, but it cannot manufacture capacity.

## 5.4 Model heterogeneity

<div class="tblwrap"><table><caption>Table 4. Per-model validity and critical recall (percent).</caption><thead><tr><th>Model</th><th>Condition</th><th>Valid</th><th>Recall</th></tr></thead><tbody><tr><td>deepseek-v4.1-flash-1017</td><td>Baseline</td><td>100</td><td>100</td></tr><tr><td>deepseek-v4.1-flash-1017</td><td>Overload</td><td>10</td><td>10</td></tr><tr><td>deepseek-v4.1-flash-1017</td><td>Overload + HAP</td><td>100</td><td>45</td></tr><tr><td>deepseek-v4.1-flash-1017</td><td>Overload + governor</td><td>100</td><td>35</td></tr><tr><td>kimi-k3.1-pro</td><td>Baseline</td><td>100</td><td>100</td></tr><tr><td>kimi-k3.1-pro</td><td>Overload</td><td>0</td><td>0</td></tr><tr><td>kimi-k3.1-pro</td><td>Overload + HAP</td><td>60</td><td>30</td></tr><tr><td>kimi-k3.1-pro</td><td>Overload + governor</td><td>100</td><td>48</td></tr><tr><td>qwen3.8-flash</td><td>Baseline</td><td>100</td><td>90</td></tr><tr><td>qwen3.8-flash</td><td>Overload</td><td>100</td><td>100</td></tr><tr><td>qwen3.8-flash</td><td>Overload + HAP</td><td>100</td><td>46</td></tr><tr><td>qwen3.8-flash</td><td>Overload + governor</td><td>100</td><td>22</td></tr></tbody></table></div>

The aggregate hides an important heterogeneity. DeepSeek and Kimi collapse under overload (recall 10% and 0%): their reasoning consumes the output budget and the response is truncated. Qwen-Flash answers all 20 batches within 2000 tokens and is at ceiling in overload (100%). The failure is therefore not universal; it is concentrated in models whose internal reasoning is charged to the same budget as the answer. HAP recovers part of the loss for the two collapsing models (45% and 30% recall) and leaves Qwen unchanged (46%); the governor is better for Kimi (48%) but worse for Qwen (22%). This is why the paper reports the mechanism and the model-specific pattern, not a single average effect.
