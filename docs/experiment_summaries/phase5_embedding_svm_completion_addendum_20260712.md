# Phase 5 Embedding + SVM Completion Addendum

Date: 2026-07-12

This addendum records the Embedding + SVM Phase 5 completion run, which was not present in the 2026-06-30 Phase 5 compendium. Following the current experimental decision, this completion run includes semantic-preserving and semantic-breaking v1 only; semantic-breaking v2-mini was not run for Embedding + SVM.

## Inputs and Model

| Item | Path |
|---|---|
| Embedding + SVM P2 original predictions | `outputs/third_round_remote_mirror_20260626/runs/second_round_extensions_20260625/embedding_svm_p2/original_test_predictions.json` |
| Semantic-preserving predictions | `outputs/third_round_phase5_embedding_svm_20260712/phase5_embedding_svm_20260712/preserving/predictions.json` |
| Semantic-breaking v1 predictions | `outputs/third_round_phase5_embedding_svm_20260712/phase5_embedding_svm_20260712/breaking_v1/predictions.json` |

Remote model used for prediction:

`/root/autodl-tmp/second_round_extensions_20260625/embedding_svm_p2/embedding_svm_train/model.pkl`

Remote encoder used by the saved model metadata:

`/root/autodl-tmp/unixcoder_local_model`

## Overall Metrics

### Semantic-Preserving

| Model | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Clone acceptance drop | Mean prob-yes drop | N clone lost |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Embedding + SVM | 94 | 71 | 55 | 0.7042 | 0.7234 | 0.1702 | 0.1550 | 21 |

### Semantic-Breaking v1

| Model | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Clone retention after breaking | Mean prob-yes drop | N clone rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Embedding + SVM | 94 | 71 | 71 | 0.0000 | 0.0000 | 1.0000 | 0.0018 | 0 |

## Per-Language Metrics

### Semantic-Preserving

| Held-out language | N pairs | N original yes | N preserving yes | Preservation consistency | Overall decision consistency | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 18 | 15 | 0.7778 | 0.8000 | 0.1088 |
| Go | 24 | 19 | 15 | 0.7368 | 0.7500 | 0.1754 |
| JavaScript | 22 | 17 | 12 | 0.6471 | 0.6818 | 0.2010 |
| Python | 23 | 17 | 13 | 0.6471 | 0.6522 | 0.1401 |

### Semantic-Breaking v1

| Held-out language | N pairs | N original yes | N variant yes | Breaking rejection rate | Overall decision change rate | Mean prob-yes drop |
|---|---:|---:|---:|---:|---:|---:|
| C++ | 25 | 18 | 18 | 0.0000 | 0.0000 | 0.0071 |
| Go | 24 | 19 | 19 | 0.0000 | 0.0000 | -0.0019 |
| JavaScript | 22 | 17 | 17 | 0.0000 | 0.0000 | 0.0060 |
| Python | 23 | 17 | 17 | 0.0000 | 0.0000 | -0.0041 |

## Interpretation

Embedding + SVM is unstable under semantic-preserving edits and insensitive to semantic-breaking edits. Under preserving edits, it loses 21 originally accepted clone decisions and shows a preservation consistency of 0.7042. Under breaking v1, it rejects none of the originally accepted broken pairs, yielding a breaking rejection rate of 0.0000 and clone retention of 1.0000.

This result strengthens the role of Embedding + SVM as a shallow representation baseline. Its behavior indicates that the embedding-based decision boundary is affected by benign surface edits, but it does not respond in the expected direction when the target-language endpoint is semantically broken.

## Generated Metric Files

| Output | Path |
|---|---|
| Preserving summary | `outputs/third_round_phase5_preserving_pilot_20260627/preserving_metrics_embedding_svm_phase5a/semantic_preserving_summary.json` |
| Preserving unified summary | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_embedding_svm_preserving/phase5_unified_embedding_svm_phase5a/phase5_unified_summary.json` |
| Preserving pair rows | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_embedding_svm_preserving/phase5_unified_embedding_svm_phase5a/preserving_pair_rows.csv` |
| Preserving per-language | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_embedding_svm_preserving/phase5_unified_embedding_svm_phase5a/preserving_per_language.csv` |
| Breaking v1 unified summary | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_embedding_svm_breaking_v1/phase5_unified_embedding_svm_breaking_v1/phase5_unified_summary.json` |
| Breaking v1 pair rows | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_embedding_svm_breaking_v1/phase5_unified_embedding_svm_breaking_v1/breaking_pair_rows.csv` |
| Breaking v1 per-language | `outputs/third_round_phase5_unified_results_20260712/phase5_unified_embedding_svm_breaking_v1/phase5_unified_embedding_svm_breaking_v1/breaking_per_language.csv` |
