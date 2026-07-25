# Public Frozen-Input Manifest

This public manifest is a disclosure-oriented companion to the local frozen-input manifest. It intentionally omits server identifiers and other machine-specific metadata.

## Frozen input categories

| Category | Public location in this package | Purpose |
|---|---|---|
| Split definitions and audits | `data/protocol_audits/` | Documents P0--P3 construction and overlap checks. |
| Released split payloads | `data/protocol_splits/` | Provides P1/P2 derived train/test JSONL data. |
| Original and counterfactual predictions | `data/statistics/`, `data/semantic_counterfactuals/` | Enables paired metric recomputation. |
| Shortcut results | `data/shortcut_audits/` | Supports RQ2 restricted-evidence analyses. |
| Phase 5 result summaries | `docs/experiment_summaries/` | Records semantic-preserving and semantic-breaking outcomes. |
| Scripts | `code/analysis/`, `code/figures/` | Computes reported statistics and figures. |

The original local frozen manifest remains retained by the authors but is not distributed because it contains machine-specific remote-host metadata. This replacement preserves the public reproducibility mapping without exposing infrastructure details.
