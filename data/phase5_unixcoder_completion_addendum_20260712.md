# Phase 5 UniXcoder Completion Addendum

Date: 2026-07-12

This addendum records the UniXcoder Phase 5 completion run, which was not present in the 2026-06-30 Phase 5 compendium. The run uses the P2 UniXcoder checkpoint and the same Phase 5 semantic-preserving, semantic-breaking v1, and semantic-breaking v2-mini inputs used for the existing GraphCodeBERT, DeepSeek-v4-flash, and Shallow Control analyses.

## Inputs and Model

| Item | Path |
|---|---|
| UniXcoder P2 original predictions | `outputs/third_round_phase5_unixcoder_20260712/original_test_predictions.json` |
| Semantic-preserving predictions | `outputs/third_round_phase5_unixcoder_20260712/phase5_unixcoder_20260712/preserving/predictions.json` |
| Semantic-breaking v1 predictions | `outputs/third_round_phase5_unixcoder_20260712/phase5_unixcoder_20260712/breaking_v1/predictions.json` |
| Semantic-breaking v2-mini predictions | `outputs/third_round_phase5_unixcoder_20260712/phase5_unixcoder_20260712/breaking_v2_mini/predictions.json` |

Remote model used for prediction:

`/root/autodl-tmp/second_round_extensions_20260625/unixcoder_p2/unixcoder_train/model`

## Overall Metrics

### Semantic-Preserving

| Model | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Clone acceptance drop | Mean prob-yes drop | N clone lost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| UniXcoder | 94 | 63 | 54 | 0.8571 | 0.9043 | 0.0957 | 0.0495 | 9 |

### Semantic-Breaking v1

| Model | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Clone retention after breaking | Mean prob-yes drop | N clone rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| UniXcoder | 94 | 63 | 62 | 0.0159 | 0.0106 | 0.9841 | -0.0004 | 1 |

### Semantic-Breaking v2-mini

| Model | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Clone retention after breaking | Mean prob-yes drop | N clone rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| UniXcoder | 32 | 23 | 23 | 0.0000 | 0.0000 | 1.0000 | 0.0001 | 0 |

## Per-Language Metrics

### Semantic-Preserving

| Held-out language | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 19 | 14 | 0.7368 | 0.8000 | 0.1320 |
| Go | 24 | 15 | 14 | 0.9333 | 0.9583 | 0.0209 |
| JavaScript | 22 | 14 | 14 | 1.0000 | 1.0000 | 0.0049 |
| Python | 23 | 15 | 12 | 0.8000 | 0.8696 | 0.0323 |

### Semantic-Breaking v1

| Held-out language | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 19 | 19 | 0.0000 | 0.0000 | 0.0001 |
| Go | 24 | 15 | 15 | 0.0000 | 0.0000 | -0.0007 |
| JavaScript | 22 | 14 | 14 | 0.0000 | 0.0000 | 0.0008 |
| Python | 23 | 15 | 14 | 0.0667 | 0.0435 | -0.0019 |

### Semantic-Breaking v2-mini

| Held-out language | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 8 | 7 | 7 | 0.0000 | 0.0000 | 0.0000 |
| Go | 8 | 6 | 6 | 0.0000 | 0.0000 | 0.0003 |
| JavaScript | 8 | 6 | 6 | 0.0000 | 0.0000 | 0.0005 |
| Python | 8 | 4 | 4 | 0.0000 | 0.0000 | -0.0003 |

## Interpretation

UniXcoder shows moderate-to-strong semantic-preserving stability, with preservation consistency of 0.8571 and overall decision consistency of 0.9043. This places it below GraphCodeBERT but above the less stable DeepSeek-v4-flash prompt variants reported in the original Phase 5 compendium.

However, UniXcoder shows almost no semantic-breaking sensitivity. Under breaking v1, only one originally accepted clone is rejected after the meaning-breaking edit, yielding a breaking rejection rate of 0.0159. Under breaking v2-mini, no originally accepted clone is rejected. This behavior is close to GraphCodeBERT's low breaking sensitivity and supports the same qualitative conclusion: representation-based detectors can be stable under surface-preserving edits while failing to reject many controlled meaning-breaking variants.

## Generated Metric Files

| Output | Path |
|---|---|
| Preserving unified summary | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_preserving/phase5_unified_unixcoder_phase5a/phase5_unified_summary.json` |
| Preserving pair rows | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_preserving/phase5_unified_unixcoder_phase5a/preserving_pair_rows.csv` |
| Preserving per-language | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_preserving/phase5_unified_unixcoder_phase5a/preserving_per_language.csv` |
| Breaking v1 unified summary | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_breaking_v1/phase5_unified_unixcoder_breaking_v1/phase5_unified_summary.json` |
| Breaking v1 pair rows | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_breaking_v1/phase5_unified_unixcoder_breaking_v1/breaking_pair_rows.csv` |
| Breaking v1 per-language | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_breaking_v1/phase5_unified_unixcoder_breaking_v1/breaking_per_language.csv` |
| Breaking v2-mini unified summary | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_breaking_v2_mini/phase5_unified_unixcoder_breaking_v2_mini/phase5_unified_summary.json` |
| Breaking v2-mini pair rows | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_breaking_v2_mini/phase5_unified_unixcoder_breaking_v2_mini/breaking_pair_rows.csv` |
| Breaking v2-mini per-language | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_unixcoder_breaking_v2_mini/phase5_unified_unixcoder_breaking_v2_mini/breaking_per_language.csv` |
