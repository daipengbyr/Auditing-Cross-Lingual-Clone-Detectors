# Shortcut / Counterfactual Experiment Summary (2026-06-25)

## Scope

- Included runs: `P2` and `P0-EB` for `GraphCodeBERT`, `UniXcoder`, `embedding+SVM`, and `DeepSeek-v4-flash`.
- Included metric families: original test metrics, shuffled-set evaluation metrics, clone-rate / probability-drop summaries, counterfactual dependency metrics (`primary` and `all_donors` in JSON/CSV), and shortcut baselines (`A1/A2/A3/A4-lite/A4-full`).
- Note: in these runs, `all_donors == primary` because `donors_per_source = 1`.

## Table 1. Original Test Metrics

| Model | Protocol | n | Precision | Recall | F1 | Accuracy | TP | FP | TN | FN |
|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek-v4-flash | P0-EB | 602 | 1.0000 | 0.7409 | 0.8511 | 0.8704 | 223 | 0 | 301 | 78 |
| GraphCodeBERT | P0-EB | 602 | 0.8618 | 0.7043 | 0.7751 | 0.7957 | 212 | 34 | 267 | 89 |
| UniXcoder | P0-EB | 602 | 0.7722 | 0.6645 | 0.7143 | 0.7342 | 200 | 59 | 242 | 101 |
| embedding+SVM | P0-EB | 602 | 0.6952 | 0.6744 | 0.6847 | 0.6894 | 203 | 89 | 212 | 98 |
| DeepSeek-v4-flash | P2 | 600 | 1.0000 | 0.5933 | 0.7448 | 0.7967 | 178 | 0 | 300 | 122 |
| GraphCodeBERT | P2 | 600 | 0.8508 | 0.7033 | 0.7701 | 0.7900 | 211 | 37 | 263 | 89 |
| UniXcoder | P2 | 600 | 0.8714 | 0.6100 | 0.7176 | 0.7600 | 183 | 27 | 273 | 117 |
| embedding+SVM | P2 | 600 | 0.6048 | 0.6733 | 0.6372 | 0.6167 | 202 | 132 | 168 | 98 |

## Table 2. Counterfactual Evaluation Metrics on Shuffled Sets

| Model | Protocol | Variant | n | Precision | Recall | F1 | Accuracy | TP | FP | TN | FN |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek-v4-flash | P0-EB | B1-random | 301 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0 | 0 | 301 | 0 |
| DeepSeek-v4-flash | P0-EB | B2-length-matched | 301 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0 | 0 | 301 | 0 |
| DeepSeek-v4-flash | P0-EB | B3-structure-matched | 301 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0 | 0 | 301 | 0 |
| GraphCodeBERT | P0-EB | B1-random | 301 | 0.0000 | 0.0000 | 0.0000 | 0.8771 | 0 | 37 | 264 | 0 |
| GraphCodeBERT | P0-EB | B2-length-matched | 301 | 0.0000 | 0.0000 | 0.0000 | 0.8904 | 0 | 33 | 268 | 0 |
| GraphCodeBERT | P0-EB | B3-structure-matched | 301 | 0.0000 | 0.0000 | 0.0000 | 0.8804 | 0 | 36 | 265 | 0 |
| UniXcoder | P0-EB | B1-random | 301 | 0.0000 | 0.0000 | 0.0000 | 0.8073 | 0 | 58 | 243 | 0 |
| UniXcoder | P0-EB | B2-length-matched | 301 | 0.0000 | 0.0000 | 0.0000 | 0.7708 | 0 | 69 | 232 | 0 |
| UniXcoder | P0-EB | B3-structure-matched | 301 | 0.0000 | 0.0000 | 0.0000 | 0.7674 | 0 | 70 | 231 | 0 |
| embedding+SVM | P0-EB | B1-random | 301 | 0.0000 | 0.0000 | 0.0000 | 0.6246 | 0 | 113 | 188 | 0 |
| embedding+SVM | P0-EB | B2-length-matched | 301 | 0.0000 | 0.0000 | 0.0000 | 0.6113 | 0 | 117 | 184 | 0 |
| embedding+SVM | P0-EB | B3-structure-matched | 301 | 0.0000 | 0.0000 | 0.0000 | 0.5914 | 0 | 123 | 178 | 0 |
| DeepSeek-v4-flash | P2 | B1-random | 300 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0 | 0 | 300 | 0 |
| DeepSeek-v4-flash | P2 | B2-length-matched | 300 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0 | 0 | 300 | 0 |
| DeepSeek-v4-flash | P2 | B3-structure-matched | 300 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0 | 0 | 300 | 0 |
| GraphCodeBERT | P2 | B1-random | 300 | 0.0000 | 0.0000 | 0.0000 | 0.9200 | 0 | 24 | 276 | 0 |
| GraphCodeBERT | P2 | B2-length-matched | 300 | 0.0000 | 0.0000 | 0.0000 | 0.8567 | 0 | 43 | 257 | 0 |
| GraphCodeBERT | P2 | B3-structure-matched | 300 | 0.0000 | 0.0000 | 0.0000 | 0.8633 | 0 | 41 | 259 | 0 |
| UniXcoder | P2 | B1-random | 300 | 0.0000 | 0.0000 | 0.0000 | 0.9033 | 0 | 29 | 271 | 0 |
| UniXcoder | P2 | B2-length-matched | 300 | 0.0000 | 0.0000 | 0.0000 | 0.9133 | 0 | 26 | 274 | 0 |
| UniXcoder | P2 | B3-structure-matched | 300 | 0.0000 | 0.0000 | 0.0000 | 0.9100 | 0 | 27 | 273 | 0 |
| embedding+SVM | P2 | B1-random | 300 | 0.0000 | 0.0000 | 0.0000 | 0.5400 | 0 | 138 | 162 | 0 |
| embedding+SVM | P2 | B2-length-matched | 300 | 0.0000 | 0.0000 | 0.0000 | 0.5067 | 0 | 148 | 152 | 0 |
| embedding+SVM | P2 | B3-structure-matched | 300 | 0.0000 | 0.0000 | 0.0000 | 0.5167 | 0 | 145 | 155 | 0 |

## Table 3. Counterfactual Dependency Metrics (Primary)

| Model | Protocol | Variant | OCA | SSR | CDFR | URFR | PFR | CPA | CPD | n_cf | n_sources |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek-v4-flash | P0-EB | B1-random | 0.7409 | 1.0000 | 1.0000 | 0.0000 | 0.7409 | 0.7409 | 0.7409 | 301 | 301 |
| DeepSeek-v4-flash | P0-EB | B2-length-matched | 0.7409 | 1.0000 | 1.0000 | 0.0000 | 0.7409 | 0.7409 | 0.7409 | 301 | 301 |
| DeepSeek-v4-flash | P0-EB | B3-structure-matched | 0.7409 | 1.0000 | 1.0000 | 0.0000 | 0.7409 | 0.7409 | 0.7409 | 301 | 301 |
| GraphCodeBERT | P0-EB | B1-random | 0.7043 | 0.8771 | 0.8962 | 0.1685 | 0.6811 | 0.6312 | 0.5294 | 301 | 301 |
| GraphCodeBERT | P0-EB | B2-length-matched | 0.7043 | 0.8904 | 0.8962 | 0.1236 | 0.6678 | 0.6312 | 0.5234 | 301 | 301 |
| GraphCodeBERT | P0-EB | B3-structure-matched | 0.7043 | 0.8804 | 0.8821 | 0.1236 | 0.6578 | 0.6213 | 0.5177 | 301 | 301 |
| UniXcoder | P0-EB | B1-random | 0.6645 | 0.8073 | 0.8000 | 0.1782 | 0.5914 | 0.5316 | 0.3672 | 301 | 301 |
| UniXcoder | P0-EB | B2-length-matched | 0.6645 | 0.7708 | 0.7450 | 0.1782 | 0.5548 | 0.4950 | 0.3498 | 301 | 301 |
| UniXcoder | P0-EB | B3-structure-matched | 0.6645 | 0.7674 | 0.7400 | 0.1782 | 0.5515 | 0.4917 | 0.3467 | 301 | 301 |
| embedding+SVM | P0-EB | B1-random | 0.6744 | 0.6246 | 0.6158 | 0.3571 | 0.5316 | 0.4153 | 0.3022 | 301 | 301 |
| embedding+SVM | P0-EB | B2-length-matched | 0.6744 | 0.6113 | 0.5714 | 0.3061 | 0.4850 | 0.3854 | 0.2933 | 301 | 301 |
| embedding+SVM | P0-EB | B3-structure-matched | 0.6744 | 0.5914 | 0.5468 | 0.3163 | 0.4718 | 0.3688 | 0.2736 | 301 | 301 |
| DeepSeek-v4-flash | P2 | B1-random | 0.5933 | 1.0000 | 1.0000 | 0.0000 | 0.5933 | 0.5933 | 0.5933 | 300 | 300 |
| DeepSeek-v4-flash | P2 | B2-length-matched | 0.5933 | 1.0000 | 1.0000 | 0.0000 | 0.5933 | 0.5933 | 0.5933 | 300 | 300 |
| DeepSeek-v4-flash | P2 | B3-structure-matched | 0.5933 | 1.0000 | 1.0000 | 0.0000 | 0.5933 | 0.5933 | 0.5933 | 300 | 300 |
| GraphCodeBERT | P2 | B1-random | 0.7033 | 0.9200 | 0.9242 | 0.0899 | 0.6767 | 0.6500 | 0.5587 | 300 | 300 |
| GraphCodeBERT | P2 | B2-length-matched | 0.7033 | 0.8567 | 0.8389 | 0.1011 | 0.6200 | 0.5900 | 0.5269 | 300 | 300 |
| GraphCodeBERT | P2 | B3-structure-matched | 0.7033 | 0.8633 | 0.8436 | 0.0899 | 0.6200 | 0.5933 | 0.5327 | 300 | 300 |
| UniXcoder | P2 | B1-random | 0.6100 | 0.9033 | 0.9180 | 0.1197 | 0.6067 | 0.5600 | 0.4344 | 300 | 300 |
| UniXcoder | P2 | B2-length-matched | 0.6100 | 0.9133 | 0.9016 | 0.0684 | 0.5767 | 0.5500 | 0.4378 | 300 | 300 |
| UniXcoder | P2 | B3-structure-matched | 0.6100 | 0.9100 | 0.9016 | 0.0769 | 0.5800 | 0.5500 | 0.4379 | 300 | 300 |
| embedding+SVM | P2 | B1-random | 0.6733 | 0.5400 | 0.4653 | 0.3061 | 0.4133 | 0.3133 | 0.2164 | 300 | 300 |
| embedding+SVM | P2 | B2-length-matched | 0.6733 | 0.5067 | 0.4356 | 0.3469 | 0.4067 | 0.2933 | 0.1689 | 300 | 300 |
| embedding+SVM | P2 | B3-structure-matched | 0.6733 | 0.5167 | 0.4505 | 0.3469 | 0.4167 | 0.3033 | 0.1779 | 300 | 300 |

## Table 4. Clone-Rate and Probability Drop Summaries

| Model | Protocol | Variant | Original clone rate | Shuffled clone rate | Clone-rate drop | Original mean prob_yes | Shuffled mean prob_yes | prob_yes drop |
|---|---|---|---|---|---|---|---|---|
| DeepSeek-v4-flash | P0-EB | B1-random | 0.7409 | 0.0000 | 0.7409 | 0.7409 | 0.0000 | 0.7409 |
| DeepSeek-v4-flash | P0-EB | B2-length-matched | 0.7409 | 0.0000 | 0.7409 | 0.7409 | 0.0000 | 0.7409 |
| DeepSeek-v4-flash | P0-EB | B3-structure-matched | 0.7409 | 0.0000 | 0.7409 | 0.7409 | 0.0000 | 0.7409 |
| GraphCodeBERT | P0-EB | B1-random | 0.7043 | 0.1229 | 0.5814 | 0.7131 | 0.1836 | 0.5294 |
| GraphCodeBERT | P0-EB | B2-length-matched | 0.7043 | 0.1096 | 0.5947 | 0.7131 | 0.1897 | 0.5234 |
| GraphCodeBERT | P0-EB | B3-structure-matched | 0.7043 | 0.1196 | 0.5847 | 0.7131 | 0.1953 | 0.5177 |
| UniXcoder | P0-EB | B1-random | 0.6645 | 0.1927 | 0.4718 | 0.6617 | 0.2945 | 0.3672 |
| UniXcoder | P0-EB | B2-length-matched | 0.6645 | 0.2292 | 0.4352 | 0.6617 | 0.3119 | 0.3498 |
| UniXcoder | P0-EB | B3-structure-matched | 0.6645 | 0.2326 | 0.4319 | 0.6617 | 0.3150 | 0.3467 |
| embedding+SVM | P0-EB | B1-random | 0.6744 | 0.3754 | 0.2990 | 0.6710 | 0.3688 | 0.3022 |
| embedding+SVM | P0-EB | B2-length-matched | 0.6744 | 0.3887 | 0.2857 | 0.6710 | 0.3777 | 0.2933 |
| embedding+SVM | P0-EB | B3-structure-matched | 0.6744 | 0.4086 | 0.2658 | 0.6710 | 0.3974 | 0.2736 |
| DeepSeek-v4-flash | P2 | B1-random | 0.5933 | 0.0000 | 0.5933 | 0.5933 | 0.0000 | 0.5933 |
| DeepSeek-v4-flash | P2 | B2-length-matched | 0.5933 | 0.0000 | 0.5933 | 0.5933 | 0.0000 | 0.5933 |
| DeepSeek-v4-flash | P2 | B3-structure-matched | 0.5933 | 0.0000 | 0.5933 | 0.5933 | 0.0000 | 0.5933 |
| GraphCodeBERT | P2 | B1-random | 0.7033 | 0.0800 | 0.6233 | 0.7214 | 0.1627 | 0.5587 |
| GraphCodeBERT | P2 | B2-length-matched | 0.7033 | 0.1433 | 0.5600 | 0.7214 | 0.1945 | 0.5269 |
| GraphCodeBERT | P2 | B3-structure-matched | 0.7033 | 0.1367 | 0.5667 | 0.7214 | 0.1887 | 0.5327 |
| UniXcoder | P2 | B1-random | 0.6100 | 0.0967 | 0.5133 | 0.6546 | 0.2202 | 0.4344 |
| UniXcoder | P2 | B2-length-matched | 0.6100 | 0.0867 | 0.5233 | 0.6546 | 0.2168 | 0.4378 |
| UniXcoder | P2 | B3-structure-matched | 0.6100 | 0.0900 | 0.5200 | 0.6546 | 0.2168 | 0.4379 |
| embedding+SVM | P2 | B1-random | 0.6733 | 0.4600 | 0.2133 | 0.6698 | 0.4534 | 0.2164 |
| embedding+SVM | P2 | B2-length-matched | 0.6733 | 0.4933 | 0.1800 | 0.6698 | 0.5009 | 0.1689 |
| embedding+SVM | P2 | B3-structure-matched | 0.6733 | 0.4833 | 0.1900 | 0.6698 | 0.4918 | 0.1779 |

## Table 5. Shortcut Baselines

| Model | Protocol | Experiment | n | Precision | Recall | F1 | Macro-F1 | Accuracy | Balanced Acc. | Predicted + Rate | Coverage | Selected C |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DeepSeek-v4-flash | P0-EB | a1_code_a_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 1.0000 | - |
| DeepSeek-v4-flash | P0-EB | a1_code_b_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| DeepSeek-v4-flash | P0-EB | a1_pair_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| DeepSeek-v4-flash | P0-EB | a2_code_a_only | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| DeepSeek-v4-flash | P0-EB | a3_code_b_only | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| DeepSeek-v4-flash | P0-EB | a4_full_surface_lexical | 602 | 0.7297 | 0.7176 | 0.7236 | 0.7259 | 0.7259 | 0.7259 | 0.4917 | - | 10.0000 |
| DeepSeek-v4-flash | P0-EB | a4_lite_surface | 602 | 0.5760 | 0.6545 | 0.6128 | 0.5845 | 0.5864 | 0.5864 | 0.5681 | - | 0.1000 |
| GraphCodeBERT | P0-EB | a1_code_a_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 1.0000 | - |
| GraphCodeBERT | P0-EB | a1_code_b_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| GraphCodeBERT | P0-EB | a1_pair_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| GraphCodeBERT | P0-EB | a2_code_a_only | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| GraphCodeBERT | P0-EB | a3_code_b_only | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| GraphCodeBERT | P0-EB | a4_full_surface_lexical | 602 | 0.7297 | 0.7176 | 0.7236 | 0.7259 | 0.7259 | 0.7259 | 0.4917 | - | 10.0000 |
| GraphCodeBERT | P0-EB | a4_lite_surface | 602 | 0.5760 | 0.6545 | 0.6128 | 0.5845 | 0.5864 | 0.5864 | 0.5681 | - | 0.1000 |
| UniXcoder | P0-EB | a1_code_a_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 1.0000 | - |
| UniXcoder | P0-EB | a1_code_b_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| UniXcoder | P0-EB | a1_pair_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| UniXcoder | P0-EB | a2_code_a_only | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| UniXcoder | P0-EB | a3_code_b_only | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| UniXcoder | P0-EB | a4_full_surface_lexical | 602 | 0.7297 | 0.7176 | 0.7236 | 0.7259 | 0.7259 | 0.7259 | 0.4917 | - | 10.0000 |
| UniXcoder | P0-EB | a4_lite_surface | 602 | 0.5760 | 0.6545 | 0.6128 | 0.5845 | 0.5864 | 0.5864 | 0.5681 | - | 0.1000 |
| embedding+SVM | P0-EB | a1_code_a_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 1.0000 | - |
| embedding+SVM | P0-EB | a1_code_b_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| embedding+SVM | P0-EB | a1_pair_hash_lookup | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| embedding+SVM | P0-EB | a2_code_a_only | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| embedding+SVM | P0-EB | a3_code_b_only | 602 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| embedding+SVM | P0-EB | a4_full_surface_lexical | 602 | 0.7297 | 0.7176 | 0.7236 | 0.7259 | 0.7259 | 0.7259 | 0.4917 | - | 10.0000 |
| embedding+SVM | P0-EB | a4_lite_surface | 602 | 0.5760 | 0.6545 | 0.6128 | 0.5845 | 0.5864 | 0.5864 | 0.5681 | - | 0.1000 |
| DeepSeek-v4-flash | P2 | a1_code_a_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| DeepSeek-v4-flash | P2 | a1_code_b_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| DeepSeek-v4-flash | P2 | a1_pair_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| DeepSeek-v4-flash | P2 | a2_code_a_only | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| DeepSeek-v4-flash | P2 | a3_code_b_only | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| DeepSeek-v4-flash | P2 | a4_full_surface_lexical | 600 | 0.7286 | 0.6533 | 0.6889 | 0.7042 | 0.7050 | 0.7050 | 0.4483 | - | 1.0000 |
| DeepSeek-v4-flash | P2 | a4_lite_surface | 600 | 0.5898 | 0.6567 | 0.6215 | 0.5987 | 0.6000 | 0.6000 | 0.5567 | - | 1.0000 |
| GraphCodeBERT | P2 | a1_code_a_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| GraphCodeBERT | P2 | a1_code_b_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| GraphCodeBERT | P2 | a1_pair_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| GraphCodeBERT | P2 | a2_code_a_only | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| GraphCodeBERT | P2 | a3_code_b_only | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| GraphCodeBERT | P2 | a4_full_surface_lexical | 600 | 0.7286 | 0.6533 | 0.6889 | 0.7042 | 0.7050 | 0.7050 | 0.4483 | - | 1.0000 |
| GraphCodeBERT | P2 | a4_lite_surface | 600 | 0.5898 | 0.6567 | 0.6215 | 0.5987 | 0.6000 | 0.6000 | 0.5567 | - | 1.0000 |
| UniXcoder | P2 | a1_code_a_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| UniXcoder | P2 | a1_code_b_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| UniXcoder | P2 | a1_pair_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| UniXcoder | P2 | a2_code_a_only | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| UniXcoder | P2 | a3_code_b_only | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| UniXcoder | P2 | a4_full_surface_lexical | 600 | 0.7286 | 0.6533 | 0.6889 | 0.7042 | 0.7050 | 0.7050 | 0.4483 | - | 1.0000 |
| UniXcoder | P2 | a4_lite_surface | 600 | 0.5898 | 0.6567 | 0.6215 | 0.5987 | 0.6000 | 0.6000 | 0.5567 | - | 1.0000 |
| embedding+SVM | P2 | a1_code_a_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| embedding+SVM | P2 | a1_code_b_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| embedding+SVM | P2 | a1_pair_hash_lookup | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | 0.0000 | - |
| embedding+SVM | P2 | a2_code_a_only | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| embedding+SVM | P2 | a3_code_b_only | 600 | 0.0000 | 0.0000 | 0.0000 | 0.3333 | 0.5000 | 0.5000 | 0.0000 | - | 0.1000 |
| embedding+SVM | P2 | a4_full_surface_lexical | 600 | 0.7286 | 0.6533 | 0.6889 | 0.7042 | 0.7050 | 0.7050 | 0.4483 | - | 1.0000 |
| embedding+SVM | P2 | a4_lite_surface | 600 | 0.5898 | 0.6567 | 0.6215 | 0.5987 | 0.6000 | 0.6000 | 0.5567 | - | 1.0000 |

## Key Findings

1. In `P2`, original-task F1 ranks `GraphCodeBERT > DeepSeek-v4-flash > UniXcoder > embedding+SVM`; the best run is `GraphCodeBERT` at `F1 = 0.7701`.
2. In `P2`, mean counterfactual partner sensitivity (`CPA`) ranks `GraphCodeBERT > DeepSeek-v4-flash > UniXcoder > embedding+SVM`, with `GraphCodeBERT` still the most partner-sensitive among the trainable models.
3. `DeepSeek-v4-flash` is now included in the same second-round bundle, so the comparison is no longer missing the API model line.
4. `B3 structure-matched` remains close to `B2 length-matched` rather than consistently harsher, which supports treating `B3` as a robustness companion rather than a dominant replacement.
5. `A4-full` remains the strongest shortcut baseline and should stay in the main paper tables as the main shallow-signal comparator.

## Output Files

- Aggregated JSON: `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/shortcut_counterfactual_experiment_metrics_20260625.json`
- Aggregated CSV: `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/shortcut_counterfactual_experiment_metrics_20260625.csv`
- This report: `/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/shortcut_counterfactual_experiment_summary_20260625.md`
