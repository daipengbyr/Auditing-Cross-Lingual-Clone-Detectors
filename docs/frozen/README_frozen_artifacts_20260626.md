# Frozen Artifacts for Third-Round Experiments

- Generated at UTC: `2026-06-26T03:15:22.801397+00:00`
- Final manifest: `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/MANIFEST_third_round_frozen_inputs_20260626.json`
- Remote raw manifest copy: `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/MANIFEST_third_round_frozen_inputs_20260626.remote.json`
- Remote frozen root: `/root/autodl-tmp/third_round_freeze_20260626`
- Freeze status: `complete`

## Purpose

This freeze package records the fixed inputs for the third-round experiments. It is designed to make the next experiments reproducible and to prevent later scripts from silently overwriting the evidence base used for the second-round conclusions.

## What Is Frozen

| Category | Count | Location | Why it matters |
|---|---:|---|---|
| Split files | 11 | AutoDL | Fixed `P2` and `P0-EB` train/valid/test/audit files |
| Prediction files | 32 | AutoDL | Original and B1/B2/B3 predictions for all four model families |
| Counterfactual sets | 56 | AutoDL | Frozen B1/B2/B3 shuffled input files |
| Metric / summary files | 88 | AutoDL | Per-run metrics and `pilot_summary.json` bundles |
| Shortcut baseline summaries | 16 | AutoDL | A1/A2/A3/A4-lite/A4-full summaries |
| Model artifacts | 60 | AutoDL | Trainable model metadata/artifacts and SVM model files |
| Experiment scripts | 16 | AutoDL | Split, prediction, evaluation, counterfactual, and runner scripts |
| Local reports/scripts | 17 | Local workspace | Aggregated reports, raw pilot summary copies, and report-generation scripts |

## Frozen Remote Roots

- `p2` split: `/root/autodl-tmp/clean_protocol_splits_v3/p2`
- `p0-eb` split: `/root/autodl-tmp/clean_protocol_splits_p0eb_20260625`
- `graphcodebert_p2` run: `/root/autodl-tmp/second_round_extensions_20260625/graphcodebert_p2`
- `graphcodebert_p0eb` run: `/root/autodl-tmp/second_round_extensions_20260625/graphcodebert_p0eb`
- `unixcoder_p2` run: `/root/autodl-tmp/second_round_extensions_20260625/unixcoder_p2`
- `unixcoder_p0eb` run: `/root/autodl-tmp/second_round_extensions_20260625/unixcoder_p0eb`
- `embedding_svm_p2` run: `/root/autodl-tmp/second_round_extensions_20260625/embedding_svm_p2`
- `embedding_svm_p0eb` run: `/root/autodl-tmp/second_round_extensions_20260625/embedding_svm_p0eb`
- `deepseek_v4_flash_p2` run: `/root/autodl-tmp/second_round_extensions_20260625/deepseek_v4_flash_p2`
- `deepseek_v4_flash_p0eb` run: `/root/autodl-tmp/second_round_extensions_20260625/deepseek_v4_flash_p0eb`
- Scripts root: `/root/autodl-tmp/CLCCD-main`

## Model / Prompt Records

- `GraphCodeBERT`: trainable transformer classifier
- `UniXcoder`: trainable transformer classifier
- `embedding+SVM`: embedding model plus SVM classifier
- `DeepSeek-v4-flash`: OpenAI-compatible API baseline
  - API base URL: `https://api.deepseek.com`
  - API model identifier: `deepseek-v4-flash`
  - API key is intentionally excluded from all freeze files.

## Write Discipline for Phase 1+

Do not write new experiment outputs into these frozen roots:

- `/root/autodl-tmp/clean_protocol_splits_v3/p2`
- `/root/autodl-tmp/clean_protocol_splits_p0eb_20260625`
- `/root/autodl-tmp/second_round_extensions_20260625`
- `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/shortcut_counterfactual_experiment_metrics_20260625.json`
- `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/shortcut_counterfactual_experiment_metrics_20260625.csv`
- `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/shortcut_counterfactual_experiment_summary_20260625.md`
- `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/shortcut_counterfactual_validate_report_20260625.md`

All new third-round outputs should use names beginning with `third_round_*`, for example:

- `/root/autodl-tmp/third_round_paired_predictions_20260626/`
- `/root/autodl-tmp/third_round_statistics_20260626/`
- local `outputs/third_round_*` files

## Integrity Summary

- Remote files hashed: `279`
- Local files hashed: `17`
- Total files hashed: `296`
- Remote missing expected files: `0`
- Local missing expected files: `0`

## Next Step

Phase 1 should read from the frozen roots above and write only to a new `third_round_*` directory. The immediate next target is exporting sample-level paired predictions for `P2` and `P0-EB` across GraphCodeBERT, UniXcoder, embedding+SVM, and DeepSeek-v4-flash.
