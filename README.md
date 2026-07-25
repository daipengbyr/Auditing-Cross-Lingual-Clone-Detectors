# Reproducibility Package

This repository accompanies *What Do Cross-Lingual Clone Detectors Really Learn? A Protocol and Semantic Counterfactual Study*.

## Contents

- `data/protocol_audits/`: P0--P3 split audit reports and split manifests.
- `data/protocol_splits/`: released P1 and P2 derived train/test JSONL splits. Each row contains Java and target-language code fragments, language labels, problem identifiers, pair labels, and hashed identifiers.
- `data/statistics/`: frozen sample-level predictions, paired counterfactual predictions, bootstrap confidence intervals, McNemar tests, and statistical manifests.
- `data/shortcut_audits/`: P2 shortcut-baseline summaries and metrics.
- `data/semantic_counterfactuals/`: sample-level outputs and unified summaries for semantic-preserving and semantic-breaking evaluations.
- `code/analysis/`: metric, paired-statistics, counterfactual, and Shallow Control evaluation scripts.
- `code/figures/`: Python scripts used to render manuscript figures.
- `docs/frozen/`: human-readable frozen-artifact documentation and a public manifest.
- `docs/experiment_summaries/`: experiment summaries and Phase 5 result compendia.
- `manuscript/`: LaTeX source, BibTeX database, standalone figure captions, and publication figure assets.

## Reproduction Scope

The package releases derived Java-to-X code-pair data, audit reports, model predictions, counterfactual variants, summary metrics, and scripts. It does **not** redistribute Project CodeNet, model weights, API credentials, SSH credentials, or server logs. Obtain the underlying corpus independently from the official Project CodeNet release, then follow the split definitions and hashes in `data/protocol_audits/` and `docs/frozen/`.

The local artifact snapshot contains P1/P2 split payloads and P0--P3 audit/manifests. The P0 and P3 raw split payloads were not retained in this public snapshot; their construction constraints and hashes remain documented in the audit/manifests, so they can be regenerated from Project CodeNet with the released protocol logic.

## Suggested Workflow

1. Inspect `docs/frozen/README_frozen_artifacts_20260626.md` and `docs/frozen/PUBLIC_MANIFEST_20260724.md`.
2. Verify P1/P2 leakage constraints using `data/protocol_audits/` and the released split files.
3. Recompute aggregate results from `data/statistics/`, `data/shortcut_audits/`, and `data/semantic_counterfactuals/` using scripts in `code/analysis/`.
4. Regenerate manuscript figures with scripts in `code/figures/` after setting the input paths described in each script.

## Data Schema and Labels

`clone` denotes a pair derived from solutions to the same programming problem; `nonclone` denotes a deliberately constructed pair from different problems. `codeA` is the Java side and `codeB` is the target-language side. Hash fields support audit and duplicate checks. Synthetic negatives are marked by `synthetic_negative: true` where applicable.

## Software and External Dependencies

The analysis scripts use Python. Model-specific reruns additionally require the original model packages/checkpoints and, for DeepSeek-v4-flash, valid provider access. No credentials are included. Package versions, prompts, and frozen input provenance are described in the included manifests and experiment summaries.

## Citation and Archiving

Before public release, replace the repository URL and version/DOI placeholders in `DATA_AVAILABILITY_STATEMENT.md`. For a permanent archival record, create a GitHub release and archive that release through Zenodo or an equivalent DOI-minting service.
