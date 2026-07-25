# Phase 5 Results Analysis (2026-06-30)

## Material Passport

- Mode: `validate`
- Skill route: `academic-research-suite` -> `experiment-agent`
- Focus: Phase 5 semantic counterfactual results interpretation
- Verification status: `ANALYZED`
- Scope boundary: This document interprets what the currently available numbers support. It does not make manuscript wording decisions for the paper.

## Analysis Scope

This analysis covers three completed Phase 5 result families:

1. `semantic-preserving` stability on a 94-pair P2-positive pilot
2. `semantic-breaking v1` sensitivity on the same 94 source pairs
3. `semantic-breaking v2-mini` sensitivity on a 32-pair stronger-output/return-targeted subset

The two formal model lines currently available are:

- GraphCodeBERT
- A4-full
- DeepSeek-v4-flash (`label_only`, `evidence_guided`, `conservative_off`)

## Executive Findings

### 1. GraphCodeBERT is highly stable under preserving edits

GraphCodeBERT achieved:

- `preservation_consistency_rate = 0.9589`
- `overall_decision_consistency_rate = 0.9468`
- `n_clone_lost = 3 / 73 original-yes pairs`

Interpretation:

- On the preserving pilot, GraphCodeBERT changed its decision very rarely.
- The result is strongest in Go and JavaScript, where preserving consistency reached `1.0`.
- Even the weaker languages, C++ and Python, remained high (`0.9000` and `0.9333` respectively).

This is a strong positive signal for semantic-preserving stability.

### 2. A4-full is moderately stable under preserving edits, but weaker than GraphCodeBERT

A4-full preserving results:

- `preservation_consistency_rate = 0.8906`
- `overall_decision_consistency_rate = 0.9255`
- `n_clone_lost = 7 / 64 original-yes pairs`

Interpretation:

- A4-full is clearly more stable than the DeepSeek prompt variants on preserving edits, but it is still weaker than GraphCodeBERT.
- The preserving weakness is concentrated mostly in C++ (`0.7500`), while JavaScript and Python remain perfectly stable on this pilot.
- This pattern is consistent with a shallow-structure baseline that can preserve many easy surface matches, but is not as uniformly robust as GraphCodeBERT.

### 3. DeepSeek-v4-flash is meaningfully less stable under preserving edits

DeepSeek-v4-flash preserving consistency was markedly lower:

- `label_only`: `0.8136`
- `evidence_guided`: `0.6939`
- `conservative_off`: `0.6949`

Interpretation:

- DeepSeek-v4-flash is more brittle than GraphCodeBERT under semantic-preserving perturbations.
- Within DeepSeek, `label_only` is the most stable prompt on preserving pairs.
- The two more elaborate prompts do not improve robustness here; they reduce it.

### 4. GraphCodeBERT is almost completely insensitive to semantic-breaking v1

GraphCodeBERT breaking-v1 results:

- `breaking_rejection_rate = 0.0274`
- `overall_decision_change_rate = 0.0213`
- `clone_retention_after_breaking = 0.9726`
- `semantic_gap = -0.0137`

Interpretation:

- GraphCodeBERT continued to say `yes` for almost all breaking variants.
- The negative `semantic_gap` is especially important: on the shared pairs, GraphCodeBERT actually said `yes` slightly more often under breaking than under preserving.
- This is not the pattern expected from a model with useful breaking sensitivity.

### 5. A4-full is also almost completely insensitive to semantic-breaking

A4-full breaking-v1 results:

- `breaking_rejection_rate = 0.0156`
- `overall_decision_change_rate = 0.0319`
- `clone_retention_after_breaking = 0.9844`
- `semantic_gap = -0.0938`

Interpretation:

- A4-full rejects only `1 / 64` original-yes breaking pairs.
- Its negative `semantic_gap` is larger in magnitude than GraphCodeBERT's, meaning the model is even more biased toward keeping the clone decision under breaking than under preserving.
- This is exactly the pattern expected from a shallow structural baseline that is not tracking the injected semantic violations.

### 6. The stronger GraphCodeBERT breaking-v2-mini result reinforces the same conclusion

GraphCodeBERT breaking-v2-mini results:

- `breaking_rejection_rate = 0.0000`
- `overall_decision_change_rate = 0.0000`
- `clone_retention_after_breaking = 1.0000`

Interpretation:

- On the 32-pair stronger-output/return-targeted subset, GraphCodeBERT did not reject a single original-yes pair.
- This matters because it weakens the simple rescue explanation that `breaking_v1` was merely too weak.
- At minimum, the current evidence supports the claim that GraphCodeBERT is not detecting the injected semantic violations in either the broader v1 set or the stronger v2-mini subset.

### 7. A4-full breaking-v2-mini remains weak, so the failure is not rescued by stronger local edits

A4-full breaking-v2-mini results:

- `breaking_rejection_rate = 0.0400`
- `overall_decision_change_rate = 0.0312`
- `clone_retention_after_breaking = 0.9600`

Interpretation:

- Even after moving to the stronger v2-mini subset, A4-full still rejects only `1 / 25` original-yes pairs.
- So the shallow lexical/surface line does not become meaningfully semantics-sensitive under the stronger breaking builder either.
- That makes A4-full a useful bridge result between GraphCodeBERT and DeepSeek: it behaves much more like GraphCodeBERT than like DeepSeek on breaking sensitivity.

### 8. DeepSeek-v4-flash shows much stronger semantic-breaking sensitivity than GraphCodeBERT or A4-full

DeepSeek-v4-flash breaking-v1 results:

- `label_only`: `breaking_rejection_rate = 0.5932`
- `evidence_guided`: `breaking_rejection_rate = 0.7959`
- `conservative_off`: `breaking_rejection_rate = 0.6610`

Interpretation:

- All three DeepSeek prompt variants reject breaking pairs far more often than GraphCodeBERT or A4-full.
- `evidence_guided` is the strongest breaking detector in the available Phase 5 results.
- `label_only` is the most preserving-stable DeepSeek prompt, but not the strongest breaking-sensitive one.

This gives a clear tradeoff pattern inside DeepSeek:

- `label_only`: better preserving stability, weaker breaking sensitivity
- `evidence_guided`: worse preserving stability, stronger breaking sensitivity
- `conservative_off`: intermediate

## Cross-Model Interpretation

## Primary Pattern

The most defensible Phase 5 pattern is:

- GraphCodeBERT: high preserving stability, very weak breaking sensitivity
- A4-full: moderately high preserving stability, very weak breaking sensitivity
- DeepSeek-v4-flash: lower preserving stability, substantially stronger breaking sensitivity

This suggests the two model families are relying on meaningfully different decision behavior:

- GraphCodeBERT appears robust to superficial or even output-targeted perturbations in the sense that it rarely changes its clone decision, but the same stability extends into semantic-breaking cases where it should ideally flip.
- A4-full shows the same qualitative failure mode, which is important because it anchors that behavior to a shallow lexical/surface baseline rather than only to one pretrained encoder.
- DeepSeek-v4-flash appears more willing to revise its decision when semantic evidence changes, but that same flexibility also makes it less stable on preserving edits.

## Strongest Headline Claim Supported by Current Data

The strongest claim currently supported is:

> In Phase 5, GraphCodeBERT and A4-full cluster together as preserving-stable but breaking-insensitive models, whereas DeepSeek-v4-flash is less preserving-stable but substantially more breaking-sensitive.

That is stronger and more defensible than a generic "LLMs are better" claim, because it is grounded in the counterfactual design.

## Statistical Interpretation Notes

### What is interpretable now

The following metrics are directly interpretable and suitable as primary Phase 5 outcomes:

- `preservation_consistency_rate`
- `overall_decision_consistency_rate`
- `breaking_rejection_rate`
- `overall_decision_change_rate`
- `clone_retention_after_breaking`
- `semantic_gap`

### What should not be foregrounded

The raw runner-level `precision / recall / f1` printed during the all-negative breaking runs should not be used as the main story, because:

- the breaking sets are intentionally constructed as negative variants
- the runner computes positive-class statistics
- therefore `precision = recall = f1 = 0` can coexist with behavior that is actually desirable for breaking rejection

The correct interpretation should instead come from rejection-oriented metrics such as `breaking_rejection_rate`.

## Reproducibility / Validation Notes

### Confidence level for the main findings

- GraphCodeBERT preserving stability: `SOLID`
- A4-full preserving stability: `SOLID`
- GraphCodeBERT breaking insensitivity: `SOLID`
- A4-full breaking insensitivity: `SOLID`
- DeepSeek-v4-flash breaking sensitivity: `SOLID`
- DeepSeek-v4-flash preserving brittleness: `CAUTION` to `SOLID`, depending on how much prompt instability the paper wants to foreground

Rationale:

- The observed model differences are large, not marginal.
- The direction of the differences is coherent across multiple prompt variants.
- GraphCodeBERT's breaking failure replicates across both `v1` and `v2-mini`.
- A4-full shows the same breaking failure pattern on both `v1` and `v2-mini`.

### Remaining limits

1. No formal confidence intervals or hypothesis tests have yet been attached to the Phase 5 metrics.
2. DeepSeek `breaking_v2-mini` was not completed as a formal comparable run.
3. `breaking_v2-mini` currently exists for GraphCodeBERT and A4-full, but not yet for DeepSeek, so it remains a partial cross-model diagnostic rather than a full benchmark.

These are limitations of completeness, not contradictions in the existing results.

## Fallacy Scan

Coverage: `11/11 checked`

### Structural fallacies

1. Simpson's Paradox: no evidence checked in current aggregate summaries; no contradiction between overall and language-level direction was found.
2. Ecological Fallacy: low risk. Claims here stay at model-run level, not user/population level.
3. Berkson's Paradox: not applicable in a strong way; this is a constructed evaluation sample, not a selected survivor-only sample.
4. Collider Bias: no obvious sign from the current reporting layer.

### Inferential fallacies

5. Base Rate Neglect: important caution. Breaking sets are all-negative counterfactual sets, so standard positive-class metrics can mislead if read naively.
6. Regression to the Mean: not applicable as a central concern.
7. Survivorship Bias: low risk for the completed formal runs; incomplete DeepSeek v2-mini is excluded from the formal result set.
8. Look-Elsewhere Effect: moderate caution. Multiple prompts are compared, but the effect sizes here are large enough that the basic qualitative conclusions are unlikely to reverse.
9. Garden of Forking Paths: moderate caution. Prompt variants and counterfactual builders evolved during the study, so final write-up should clearly separate confirmatory versus exploratory components.

### Causal fallacies

10. Correlation != Causation: caution. These results show evaluation behavior under constructed counterfactuals; they do not, by themselves, prove internal causal mechanisms of the models.
11. Reverse Causality: not relevant here.

## Recommended Write-Up Position

If you want the cleanest Phase 5 narrative in the paper, the most defensible framing is:

1. Preserve the three-way contrast: GraphCodeBERT, A4-full, and DeepSeek-v4-flash.
2. Use GraphCodeBERT + A4-full `breaking_v2-mini` as diagnostic reinforcement, not as the sole main table.
3. Present A4-full as the shallow-structure anchor for interpreting breaking sensitivity.
4. Present DeepSeek prompt variants as an internal tradeoff study:
   - `label_only` is best for preserving stability
   - `evidence_guided` is best for breaking sensitivity
5. Avoid treating API-runner `f1 = 0` on breaking sets as a failure; explain why rejection-oriented metrics are the proper interpretation.

## Bottom Line

The current Phase 5 evidence supports a strong and publishable contrast:

- GraphCodeBERT and A4-full are both fairly stable under semantic-preserving edits but do not meaningfully react to semantic-breaking edits.
- DeepSeek-v4-flash is less stable under preserving edits but much more responsive to semantic-breaking edits.

That three-way contrast is the most important Phase 5 result presently in the workspace.
