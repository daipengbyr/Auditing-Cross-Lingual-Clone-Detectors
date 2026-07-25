# Phase 5 All Metrics Compendium (2026-06-30)

## Scope

This document consolidates all completed Phase 5 results currently available in the workspace:

- Phase 5A semantic-preserving pilot
- Phase 5B semantic-breaking v1
- Phase 5B semantic-breaking v2-mini
- GraphCodeBERT
- A4-full
- DeepSeek-v4-flash (`label_only`, `evidence_guided`, `conservative_off`)

Incomplete or intentionally aborted runs are not treated as formal results.

## Artifact Inventory

### Phase 5A Preserving Pilot Inputs

- Source manifest: [semantic_preserving_manifest.json](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/semantic_preserving_manifest.json)
- Source model input: [semantic_preserving_model_input.jsonl](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/semantic_preserving_model_input.jsonl)
- Language summary: [semantic_preserving_lang_summary.csv](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/semantic_preserving_lang_summary.csv)

### Phase 5B Breaking v1 Inputs

- Source manifest: [semantic_breaking_manifest.json](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_breaking_pilot_20260628/semantic_breaking_manifest.json)
- Source model input: [semantic_breaking_model_input.jsonl](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_breaking_pilot_20260628/semantic_breaking_model_input.jsonl)
- Language summary: [semantic_breaking_lang_summary.csv](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_breaking_pilot_20260628/semantic_breaking_lang_summary.csv)

### Phase 5B Breaking v2-mini Inputs

- Source manifest: [semantic_breaking_v2_manifest.json](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_breaking_v2_mini_20260628/semantic_breaking_v2_manifest.json)
- Source model input: [semantic_breaking_v2_model_input.jsonl](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_breaking_v2_mini_20260628/semantic_breaking_v2_model_input.jsonl)
- Language summary: [semantic_breaking_v2_lang_summary.csv](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_breaking_v2_mini_20260628/semantic_breaking_v2_lang_summary.csv)

## Counterfactual Construction Summary

### Preserving Pilot Construction

| Language | Attempted | Selected | Auto-pass | Manual-required | Skip |
|---|---:|---:|---:|---:|---:|
| Python | 30 | 23 | 23 | 0 | 7 |
| C++ | 27 | 25 | 14 | 11 | 2 |
| Go | 30 | 24 | 0 | 24 | 6 |
| JavaScript | 30 | 22 | 22 | 0 | 8 |
| Total | 117 | 94 | 59 | 35 | 23 |

### Breaking v1 Construction

| Language | Selected | Auto-pass | Manual-required | Skip |
|---|---:|---:|---:|---:|
| Python | 23 | 23 | 0 | 0 |
| C++ | 25 | 14 | 11 | 0 |
| Go | 24 | 0 | 24 | 0 |
| JavaScript | 22 | 22 | 0 | 0 |
| Total | 94 | 59 | 35 | 0 |

### Breaking v2-mini Construction

| Language | Attempted | Selected | Auto-pass | Manual-required | Skip |
|---|---:|---:|---:|---:|---:|
| Python | 9 | 8 | 8 | 0 | 1 |
| C++ | 8 | 8 | 5 | 3 | 0 |
| Go | 8 | 8 | 0 | 8 | 0 |
| JavaScript | 10 | 8 | 8 | 0 | 2 |
| Total | 35 | 32 | 21 | 11 | 3 |

## Phase 5A Preserving Metrics

### Aggregate Results

| Model / Prompt | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Clone acceptance drop | Mean prob-yes drop | N clone lost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GraphCodeBERT | 94 | 73 | 72 | 0.9589 | 0.9468 | 0.0106 | 0.0158 | 3 |
| A4-full | 94 | 64 | 57 | 0.8906 | 0.9255 | 0.0745 | 0.0258 | 7 |
| DeepSeek-v4-flash `label_only` | 94 | 59 | 61 | 0.8136 | 0.7447 | -0.0213 | NA | 11 |
| DeepSeek-v4-flash `evidence_guided` | 94 | 49 | 46 | 0.6939 | 0.7128 | 0.0319 | NA | 15 |
| DeepSeek-v4-flash `conservative_off` | 94 | 59 | 54 | 0.6949 | 0.6702 | 0.0532 | NA | 18 |

### Per-Language Preserving Results

#### GraphCodeBERT

| Lang | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Clone acceptance drop | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 20 | 19 | 0.9000 | 0.8800 | 0.0400 | 0.0733 |
| Go | 24 | 19 | 19 | 1.0000 | 1.0000 | 0.0000 | 0.0099 |
| JavaScript | 22 | 19 | 19 | 1.0000 | 1.0000 | 0.0000 | -0.0191 |
| Python | 23 | 15 | 15 | 0.9333 | 0.9130 | 0.0000 | -0.0073 |

#### A4-full

| Lang | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Clone acceptance drop | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 20 | 15 | 0.7500 | 0.8000 | 0.2000 | 0.0763 |
| Go | 24 | 16 | 14 | 0.8750 | 0.9167 | 0.0833 | 0.0187 |
| JavaScript | 22 | 15 | 15 | 1.0000 | 1.0000 | 0.0000 | -0.0010 |
| Python | 23 | 13 | 13 | 1.0000 | 1.0000 | 0.0000 | 0.0038 |

#### DeepSeek-v4-flash `label_only`

| Lang | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Clone acceptance drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 15 | 14 | 0.6667 | 0.6400 | 0.0400 |
| Go | 24 | 19 | 18 | 0.8421 | 0.7917 | 0.0417 |
| JavaScript | 22 | 13 | 14 | 0.9231 | 0.8636 | -0.0455 |
| Python | 23 | 12 | 15 | 0.8333 | 0.6957 | -0.1304 |

#### DeepSeek-v4-flash `evidence_guided`

| Lang | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Clone acceptance drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 12 | 13 | 0.6667 | 0.6400 | -0.0400 |
| Go | 24 | 16 | 14 | 0.7500 | 0.7500 | 0.0833 |
| JavaScript | 22 | 10 | 10 | 0.8000 | 0.8182 | 0.0000 |
| Python | 23 | 11 | 9 | 0.5455 | 0.6522 | 0.0870 |

#### DeepSeek-v4-flash `conservative_off`

| Lang | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Clone acceptance drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 15 | 13 | 0.6000 | 0.6000 | 0.0800 |
| Go | 24 | 15 | 15 | 0.7333 | 0.6667 | 0.0000 |
| JavaScript | 22 | 14 | 13 | 0.7857 | 0.7727 | 0.0455 |
| Python | 23 | 15 | 13 | 0.6667 | 0.6522 | 0.0870 |

## Phase 5B Breaking v1 Metrics

### Aggregate Results

| Model / Prompt | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Clone retention after breaking | Mean prob-yes drop | N clone rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GraphCodeBERT | 94 | 73 | 71 | 0.0274 | 0.0213 | 0.9726 | 0.0096 | 2 |
| A4-full | 94 | 64 | 65 | 0.0156 | 0.0319 | 0.9844 | 0.0028 | 1 |
| DeepSeek-v4-flash `label_only` | 94 | 59 | 29 | 0.5932 | 0.4255 | 0.4068 | NA | 35 |
| DeepSeek-v4-flash `evidence_guided` | 94 | 49 | 17 | 0.7959 | 0.4894 | 0.2041 | NA | 39 |
| DeepSeek-v4-flash `conservative_off` | 94 | 59 | 30 | 0.6610 | 0.5213 | 0.3390 | NA | 39 |

### GraphCodeBERT Preserving-vs-Breaking Contrast (v1)

| Metric | Value |
|---|---:|
| N shared pairs | 94 |
| N original yes shared | 73 |
| Preserve yes / break no rate | 0.0274 |
| Directional success rate | 0.0274 |
| Directional failure rate | 0.0411 |
| Preserving yes rate shared | 0.9589 |
| Breaking yes rate shared | 0.9726 |
| Semantic gap | -0.0137 |

### A4-full Preserving-vs-Breaking Contrast (v1)

| Metric | Value |
|---|---:|
| N shared pairs | 94 |
| N original yes shared | 64 |
| Preserve yes / break no rate | 0.0156 |
| Directional success rate | 0.0156 |
| Directional failure rate | 0.1094 |
| Preserving yes rate shared | 0.8906 |
| Breaking yes rate shared | 0.9844 |
| Semantic gap | -0.0938 |

### Per-Language Breaking v1 Results

#### GraphCodeBERT

| Lang | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 20 | 20 | 0.0000 | 0.0000 | -0.0009 |
| Go | 24 | 19 | 19 | 0.0000 | 0.0000 | 0.0026 |
| JavaScript | 22 | 19 | 18 | 0.0526 | 0.0455 | 0.0353 |
| Python | 23 | 15 | 14 | 0.0667 | 0.0435 | 0.0037 |

#### A4-full

| Lang | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 20 | 20 | 0.0000 | 0.0000 | 0.0004 |
| Go | 24 | 16 | 16 | 0.0000 | 0.0000 | 0.0033 |
| JavaScript | 22 | 15 | 15 | 0.0000 | 0.0000 | 0.0050 |
| Python | 23 | 13 | 14 | 0.0769 | 0.1304 | 0.0027 |

#### DeepSeek-v4-flash `label_only`

| Lang | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate |
|---|---:|---:|---:|---:|---:|
| C++ | 25 | 15 | 7 | 0.6667 | 0.4800 |
| Go | 24 | 19 | 10 | 0.5263 | 0.4583 |
| JavaScript | 22 | 13 | 6 | 0.6154 | 0.4091 |
| Python | 23 | 12 | 6 | 0.5833 | 0.3478 |

#### DeepSeek-v4-flash `evidence_guided`

| Lang | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate |
|---|---:|---:|---:|---:|---:|
| C++ | 25 | 12 | 3 | 0.8333 | 0.4400 |
| Go | 24 | 16 | 5 | 0.8125 | 0.6250 |
| JavaScript | 22 | 10 | 4 | 0.7000 | 0.3636 |
| Python | 23 | 11 | 5 | 0.8182 | 0.5217 |

#### DeepSeek-v4-flash `conservative_off`

| Lang | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate |
|---|---:|---:|---:|---:|---:|
| C++ | 25 | 15 | 6 | 0.8000 | 0.6000 |
| Go | 24 | 15 | 10 | 0.6667 | 0.6250 |
| JavaScript | 22 | 14 | 6 | 0.6429 | 0.4545 |
| Python | 23 | 15 | 8 | 0.5333 | 0.3913 |

## Phase 5B Breaking v2-mini Metrics

### GraphCodeBERT and A4-full

| Model / Prompt | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Clone retention after breaking | Mean prob-yes drop | N clone rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GraphCodeBERT `breaking_v2-mini` | 32 | 26 | 26 | 0.0000 | 0.0000 | 1.0000 | 0.0029 | 0 |
| A4-full `breaking_v2-mini` | 32 | 25 | 24 | 0.0400 | 0.0312 | 0.9600 | 0.0021 | 1 |

### GraphCodeBERT Breaking v2-mini Per Language

| Lang | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 8 | 8 | 8 | 0.0000 | 0.0000 | 0.0000 |
| Go | 8 | 7 | 7 | 0.0000 | 0.0000 | -0.0001 |
| JavaScript | 8 | 7 | 7 | 0.0000 | 0.0000 | 0.0076 |
| Python | 8 | 4 | 4 | 0.0000 | 0.0000 | 0.0042 |

### A4-full Breaking v2-mini Per Language

| Lang | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 8 | 8 | 8 | 0.0000 | 0.0000 | -0.0030 |
| Go | 8 | 5 | 5 | 0.0000 | 0.0000 | 0.0072 |
| JavaScript | 8 | 7 | 7 | 0.0000 | 0.0000 | -0.0020 |
| Python | 8 | 5 | 4 | 0.2000 | 0.1250 | 0.0060 |

## Notes on Incomplete / Exploratory Runs

- DeepSeek-v4-flash `breaking_v2-mini` was intentionally stopped before completion after exploratory evidence suggested strong rejection behavior already at `label_only`; it is not included as a formal comparable result set here.
- `precision`, `recall`, and `f1` emitted by the prompt runner on all-negative breaking sets are not substantively interpretable as primary Phase 5 metrics, because those statistics are computed with the positive class (`clone`) as the target. The formal interpretation in this phase should rely on:
  - `breaking_rejection_rate`
  - `overall_decision_change_rate`
  - `clone_retention_after_breaking`
  - `n_clone_rejected`

## Source Files for Formal Result Reuse

### Preserving Summaries

- [semantic_preserving_summary.json (GraphCodeBERT)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/preserving_metrics_graphcodebert_phase5a/semantic_preserving_summary.json)
- [semantic_preserving_summary.json (A4-full)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/preserving_metrics_a4_full_phase5a/semantic_preserving_summary.json)
- [semantic_preserving_summary.json (DeepSeek label_only)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/preserving_metrics_deepseek_v4_flash_label_only/semantic_preserving_summary.json)
- [semantic_preserving_summary.json (DeepSeek evidence_guided)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/preserving_metrics_deepseek_v4_flash_evidence_guided/semantic_preserving_summary.json)
- [semantic_preserving_summary.json (DeepSeek conservative_off)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/preserving_metrics_deepseek_v4_flash_conservative_off/semantic_preserving_summary.json)

### Unified Breaking Summaries

- [phase5_unified_summary.json (GraphCodeBERT v1)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260628/phase5_unified_graphcodebert_phase5b/phase5_unified_summary.json)
- [phase5_unified_summary.json (GraphCodeBERT v2-mini)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260628/phase5_unified_graphcodebert_breaking_v2_mini/phase5_unified_summary.json)
- [phase5_unified_summary.json (A4-full v1)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260630/phase5_unified_a4_full_phase5b/phase5_unified_summary.json)
- [phase5_unified_summary.json (A4-full v2-mini)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260630/phase5_unified_a4_full_breaking_v2_mini/phase5_unified_summary.json)
- [phase5_unified_summary.json (DeepSeek label_only v1)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260630/phase5_unified_deepseek_v4_flash_breaking_v1_label_only/phase5_unified_summary.json)
- [phase5_unified_summary.json (DeepSeek evidence_guided v1)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260630/phase5_unified_deepseek_v4_flash_breaking_v1_evidence_guided/phase5_unified_summary.json)
- [phase5_unified_summary.json (DeepSeek conservative_off v1)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260630/phase5_unified_deepseek_v4_flash_breaking_v1_conservative_off/phase5_unified_summary.json)
