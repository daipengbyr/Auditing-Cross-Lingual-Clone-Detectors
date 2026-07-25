# P0-P3 跨语言代码克隆检测实验流程与结果总结

## Material Passport

- Origin Skill: academic-research-suite / experiment-agent
- Origin Mode: validate
- Origin Date: 2026-06-23
- Verification Status: ANALYZED
- Version Label: p0_p3_pipeline_summary_v1
- Overall Confidence: CAUTION

## 1. 文档目的

本文档总结从早期 R1/R5 复现、数据泄露发现，到 P0-P3 clean-split 重构和 P3-multi 扩展的完整实验过程。目标是让后续分析者能够回答四个问题：

1. 使用了什么数据、模型与运行设置；
2. 为什么从原始 R1/R5 转向协议审计；
3. 各模型在 P0-P3 和 P3-multi 上得到什么结果；
4. 哪些结果可以进入论文主结论，哪些只能作为诊断性证据。

本次工作读取并交叉核对了本地脚本、已有总结文件，以及 AutoDL 上现存的 `metrics.json`、`summary.json` 和 `audit.json`。没有重新训练模型，因此状态为 `ANALYZED`，不是重新运行后的 `VERIFIED`。

## 2. 总体结论

P0-P3 实验已经覆盖五种模型设置：GraphCodeBERT、UniXcoder fine-tuned classifier、UniXcoder embedding + SVM、DeepSeek-R1-Distill-Qwen-7B，以及 DeepSeek-v4-flash API。五种设置均完成了 P3-multi，其中本地 DeepSeek-7B 的性能较低。

最稳定的观察是：

- GraphCodeBERT、UniXcoder 和 embedding + SVM 在 P0 上很高，但在 clean protocols 上明显下降；
- DeepSeek-v4-flash 在 P0、P1、P2 和 P3-multi 上保持较高性能，P3-multi macro-F1 为 `0.8852`；
- 本地 DeepSeek-R1-Distill-Qwen-7B 的主要问题是低 recall，而不是从 P0 到 clean protocol 的性能坍塌；
- P0 的 train-test contamination 已由 audit 直接确认；
- P1 最终 audit 同时满足 problem overlap = 0，因此不能再被解释成“仅去掉 exact-code overlap”的纯粹中间层；
- clean protocols 重构了负样本，因此 P0 与 P1/P2 的差异同时包含泄露移除、problem partition 和负样本分布变化，不能把全部性能下降单因果归因于 leakage。

## 3. 实验时间线

| 阶段 | 内容 | 作用 | 可信度定位 |
|---|---|---|---|
| A | Qwen2.5-Coder-7B + PEA-LLM 的 R1/R5 复现 | 检查 prompt-only 与结构化证据的差异 | 前期诊断 |
| B | GraphCodeBERT、UniXcoder、embedding + SVM 与 DeepSeek 的原始数据实验 | 比较不同模型行为 | 前期诊断 |
| C | GraphCodeBERT leakage audit | 发现 problem、exact code 和训练样本污染 | 直接审计证据 |
| D | 构建 P0-P3，并平衡 P1/P2/P3 的正负样本 | 建立协议化评估 | 正式实验基础 |
| E | GraphCodeBERT、UniXcoder、embedding + SVM、本地 DeepSeek-7B 和 DeepSeek-v4-flash 跑 P0-P3 | 比较协议敏感性 | 主结果，单次运行 |
| F | 将 P3 从单个 Rust 测试扩展为 10 个 held-out language | 估计跨语言迁移均值和方差 | 主结果扩展 |

## 4. 数据集

### 4.1 数据来源与基本组成

实验使用准备好的 `java_cn.json`/`data_java_cn.json`，它来源于 Project CodeNet 处理流程，但各模型运行时并未直接从原始 CodeNet 目录重新抽取数据。

- 总样本数：`6,000`
- clone：`3,000`
- non-clone：`3,000`
- 源语言：Java
- 目标语言：C、C#、C++、Go、JavaScript、OCaml、PHP、Python、Ruby、Rust
- 每个 Java-X language pair：`600` 条

### 4.2 Clean protocol 的负样本构造

P1、P2 和 P3 先保留同 problem 的正类 pair，再在各自 split 内将不同 problem 的 CodeA/CodeB 重新配对，生成与正类数量相同的 synthetic non-clone。这样解决了 strict split 下 test 单类的问题，也保证负样本不会跨 split 引入代码。

这个设计使 clean test 平衡且可评估，但同时带来一个必须保留的解释限制：P0 使用原始负样本，P1-P3 使用 partition 内重构负样本。因此 P0 与 clean protocols 的差异不是只改变 split 边界。

## 5. 数据协议与审计结果

### 5.1 实际使用的协议

| Protocol | Train | Valid | Test | Test label | Intended definition |
|---|---:|---:|---:|---|---|
| P0 | 4,775 | 610 | 615 | 301 clone / 314 non-clone | pair-random |
| P1 | 4,800 | 600 | 600 | 300 / 300 | balanced code-disjoint |
| P2 | 4,800 | 600 | 600 | 300 / 300 | balanced problem-disjoint |
| P3-single | 4,320 | 540 | 60 | 30 / 30 | Rust held out + problem-disjoint |
| P3-multi | 4,320/fold | 540/fold | 60/fold | 30 / 30 | 分别留出 10 种目标语言 |

### 5.2 Train-test leakage audit

| Protocol | Problem overlap | Exact code overlap | Pair overlap | Test rows with train-seen code | Audit interpretation |
|---|---:|---:|---:|---:|---|
| P0 | 432 | 573 | 0 | 615/615 | 高度污染 |
| P1 | 0 | 0 | 0 | 0/600 | 通过，但实际也 problem-disjoint |
| P2 | 0 | 0 | 0 | 0/600 | 通过 |
| P3-single | 0 | 0 | 0 | 0/60 | 通过；Rust 未出现在 train |
| P3-multi | 0 in all folds | 0 in all folds | 0 in all folds | 0/60 per fold | 10 个 held-out folds 全部通过 |

P3-multi 的 10 个 fold 均满足：held-out language 在 train 中计数为 0、train-test problem overlap 为 0、exact code overlap 为 0。

### 5.3 P1 的协议偏差

P1 的构建目标是允许 problem overlap、只禁止 normalized exact-code overlap。但在当前数据上，按代码 hash connected component 划分后，最终 audit 显示 P1 的 problem overlap 也为 0。这意味着：

- P1 是一个有效 clean split；
- P1 与 P2 使用不同 partition，能够提供 clean-result 稳健性证据；
- 但 `P0 -> P1 -> P2` 不能被严格解释成逐层移除 exact-code leakage、再移除 problem leakage 的因果阶梯。

## 6. 模型与运行设置

### 6.1 GraphCodeBERT

- Base model：`microsoft/graphcodebert-base` 的本地镜像
- 任务形式：pair sequence classification，输入为两段原始代码及语言标签
- Epochs：3
- Train batch size：8
- Prediction batch size：16
- Learning rate：`2e-5`（训练脚本默认值）
- Maximum length：256
- 每个 protocol 独立 fine-tune

GraphCodeBERT 原始 protocol 结果目录曾丢失；当前 P0-P3 指标位于 `graphcodebert_protocol_metrics_restored_20260622`。因此指标可用于汇总，但原始训练 artifact 的完整可追溯性弱于其他模型。

### 6.2 UniXcoder Fine-tuned Classifier

- Base model：`microsoft/unixcoder-base` 的本地镜像
- 训练代码：与 GraphCodeBERT 相同的 pair sequence-classification pipeline
- Epochs：3
- Train batch size：8
- Prediction batch size：16
- Learning rate：`2e-5`
- Maximum length：256
- 每个 protocol 或 P3 held-out fold 独立 fine-tune

### 6.3 UniXcoder Embedding + SVM

- Encoder：冻结的 `microsoft/unixcoder-base`
- Maximum length：256
- Pooling：attention-mask mean pooling
- Pair feature：`[A, B, |A-B|, A*B]`
- Feature dimension：3,072
- Classifier：`StandardScaler + LinearSVC`
- `random_state=42`，`max_iter=5000`

### 6.4 DeepSeek-R1-Distill-Qwen-7B

- Model：本地 `DeepSeek-R1-Distill-Qwen-7B`
- 方式：HF causal zero-shot prompt，不进行 protocol-specific fine-tuning
- Prompt style：direct
- Batch size：4
- Maximum input length：2,048
- Maximum new tokens：32

由于该模型不使用 P0-P3 train split，协议对它表示不同 test set，而不是逐步移除其训练集泄露。

### 6.5 DeepSeek-v4-flash

- Provider：DeepSeek OpenAI-compatible API
- Model：`deepseek-v4-flash`
- 方式：zero-shot binary prompt
- Temperature：0
- Backend：chat completion
- Reasoning：`thinking.type=disabled`
- 输出：严格解析 `yes/no`

它同样没有在 P0-P3 train split 上训练，因此只能讨论对不同协议测试集的稳健性，不能把 P0-P2 差异解释成模型训练 contamination 的变化。

## 7. 早期 R1/R5：保留，但不进入主结果

### 7.1 为什么保留

R1/R5 记录了 PEA-LLM 方法复现和模型替换过程，也直接促成了 leakage audit。删掉这段历史会让 P0-P3 的研究动机显得突兀，因此应作为“前期实验与协议问题发现”保留。

### 7.2 Qwen2.5-Coder-7B + PEA-LLM

| Setting | Precision | Recall | F1 | Accuracy |
|---|---:|---:|---:|---:|
| Prompt-only | 0.5369 | 0.1457 | 0.2292 | 0.5100 |
| Full PEA-LLM | 0.5801 | 0.1823 | 0.2775 | 0.5252 |
| Full - Prompt | +0.0432 | +0.0366 | +0.0483 | +0.0152 |

R5 中，full PEA-LLM 在 JavaScript、PHP、Ruby 和 Python 上的 F1 增益较大，Rust 下降 `0.0278`。整体瓶颈是 recall 很低。

### 7.3 早期模型比较

| Model/variant | Overall F1 | Interpretation |
|---|---:|---|
| GraphCodeBERT | 0.9931 | 训练后对完整 6,000 条源文件预测，包含训练样本 |
| UniXcoder classifier | 0.9985 | 同上 |
| UniXcoder embedding + SVM | 0.9898 | 同上 |
| DeepSeek-7B direct prompt | 0.5908 | 未训练，但在同一完整数据文件上 zero-shot 推理 |
| DeepSeek-7B few-shot-4 | 0.5621 | 低于 direct prompt |
| DeepSeek-7B chain-of-evidence | 0.0852 | recall 坍塌 |

### 7.4 为什么不能作为正式 test 结果

早期 GraphCodeBERT、UniXcoder、embedding + SVM 和 PEA-LLM runner 都先从 6,000 条数据内部划分训练/验证，再对完整 6,000 条文件做预测和汇总。因此结果包含训练样本，不是独立 test-only evaluation。

此外，早期 `split_by_hash` audit 的 split 为 `4829/561/610`，而正式 P0 为 `4775/610/615`。两者都属于 pair-level contaminated protocol，但具体 split 不同，不能把早期 R1/R5 数值直接与 P0 数值相减。

因此 R1/R5 的正确定位是：

- 可用于记录方法开发和发现异常；
- 可用于说明结构化证据在该训练流程中带来小幅增益；
- 不可用于声称跨问题或跨代码泛化；
- 不进入 P0-P3 主结果表，也不参与统计显著性比较。

## 8. P0-P3 正式结果

### 8.1 完整指标

| Model | Protocol | N | Precision | Recall | F1 | Accuracy |
|---|---|---:|---:|---:|---:|---:|
| GraphCodeBERT | P0 | 615 | 1.0000 | 0.9701 | 0.9848 | 0.9854 |
| GraphCodeBERT | P1 | 600 | 0.8125 | 0.5200 | 0.6341 | 0.7000 |
| GraphCodeBERT | P2 | 600 | 0.8068 | 0.5567 | 0.6588 | 0.7117 |
| GraphCodeBERT | P3-single | 60 | 0.8333 | 0.5000 | 0.6250 | 0.7000 |
| UniXcoder | P0 | 615 | 1.0000 | 0.9834 | 0.9916 | 0.9919 |
| UniXcoder | P1 | 600 | 0.8658 | 0.6667 | 0.7533 | 0.7817 |
| UniXcoder | P2 | 600 | 0.8585 | 0.5867 | 0.6970 | 0.7450 |
| UniXcoder | P3-single | 60 | 0.7619 | 0.5333 | 0.6275 | 0.6833 |
| Embedding + SVM | P0 | 615 | 0.9497 | 0.9402 | 0.9449 | 0.9463 |
| Embedding + SVM | P1 | 600 | 0.6304 | 0.6367 | 0.6335 | 0.6317 |
| Embedding + SVM | P2 | 600 | 0.6048 | 0.6733 | 0.6372 | 0.6167 |
| Embedding + SVM | P3-single | 60 | 0.6316 | 0.4000 | 0.4898 | 0.5833 |
| DeepSeek-7B | P0 | 615 | 0.4538 | 0.1794 | 0.2571 | 0.4927 |
| DeepSeek-7B | P1 | 600 | 0.5556 | 0.2167 | 0.3118 | 0.5217 |
| DeepSeek-7B | P2 | 600 | 0.5620 | 0.2267 | 0.3230 | 0.5250 |
| DeepSeek-7B | P3-single | 60 | 0.6667 | 0.2000 | 0.3077 | 0.5500 |
| DeepSeek-v4-flash | P0 | 615 | 1.0000 | 0.8638 | 0.9269 | 0.9333 |
| DeepSeek-v4-flash | P1 | 600 | 1.0000 | 0.8367 | 0.9111 | 0.9183 |
| DeepSeek-v4-flash | P2 | 600 | 1.0000 | 0.7967 | 0.8868 | 0.8983 |
| DeepSeek-v4-flash | P3-single | 60 | 1.0000 | 0.8667 | 0.9286 | 0.9333 |

### 8.2 Protocol sensitivity

`Delta` 定义为 `F1(P0) - F1(Pk)`；正值表示相对 P0 下降。

| Model | P0 F1 | P1 F1 | Delta P0-P1 | P2 F1 | Delta P0-P2 |
|---|---:|---:|---:|---:|---:|
| GraphCodeBERT | 0.9848 | 0.6341 | +0.3507 | 0.6588 | +0.3260 |
| UniXcoder | 0.9916 | 0.7533 | +0.2383 | 0.6970 | +0.2946 |
| Embedding + SVM | 0.9449 | 0.6335 | +0.3114 | 0.6372 | +0.3077 |
| DeepSeek-7B | 0.2571 | 0.3118 | -0.0547 | 0.3230 | -0.0659 |
| DeepSeek-v4-flash | 0.9269 | 0.9111 | +0.0158 | 0.8868 | +0.0401 |

对三个 trainable encoder baselines，P0 到 P2 的绝对 F1 下降为 `0.2946-0.3260`。这与 P0 contamination 审计一致，但由于负样本构造和 problem partition 同时变化，下降幅度不能解释为 leakage 的纯净因果效应。

DeepSeek-v4-flash 的 precision 在所有单协议测试中均为 1.0，主要错误来自 false negatives。该模式值得在后续实验中继续检查，因为它可能反映保守判别倾向，也可能受当前 synthetic negatives 难度影响。

## 9. P3-Multi：10 个 Held-out Language

### 9.1 Per-language F1

| Held-out language | GraphCodeBERT | UniXcoder | Embedding + SVM | DeepSeek-7B | DeepSeek-v4-flash |
|---|---:|---:|---:|---:|---:|
| C | 0.7451 | 0.8519 | 0.6667 | 0.4545 | 0.9091 |
| C++ | 0.6939 | 0.7600 | 0.6071 | 0.4000 | 0.8679 |
| C# | 0.6122 | 0.6087 | 0.6176 | 0.2857 | 0.9286 |
| Go | 0.7059 | 0.7407 | 0.6575 | 0.3158 | 0.9474 |
| JavaScript | 0.5714 | 0.7451 | 0.6557 | 0.1538 | 0.8889 |
| OCaml | 0.8000 | 0.7170 | 0.6061 | 0.3000 | 0.8679 |
| PHP | 0.6316 | 0.6792 | 0.6377 | 0.3636 | 0.8679 |
| Python | 0.6667 | 0.8214 | 0.6000 | 0.1860 | 0.8000 |
| Ruby | 0.6275 | 0.6122 | 0.6250 | 0.4167 | 0.8462 |
| Rust | 0.5600 | 0.6400 | 0.4898 | 0.3077 | 0.9286 |

### 9.2 Macro-average 与跨语言波动

| Model | Macro Precision | Macro Recall | Macro F1 | Macro Accuracy | F1 population SD |
|---|---:|---:|---:|---:|---:|
| GraphCodeBERT | 0.7942 | 0.5700 | 0.6614 | 0.7100 | 0.0722 |
| UniXcoder | 0.8604 | 0.6200 | 0.7176 | 0.7600 | 0.0790 |
| Embedding + SVM | 0.6016 | 0.6467 | 0.6163 | 0.6033 | 0.0477 |
| DeepSeek-7B | 0.5599 | 0.2267 | 0.3184 | 0.5233 | 0.0911 |
| DeepSeek-v4-flash | 1.0000 | 0.7967 | 0.8852 | 0.8983 | 0.0423 |

在这 10 个 held-out folds 上，DeepSeek-v4-flash 的 macro-F1 最高且跨语言标准差最小；trainable encoder 中 UniXcoder 最好。Embedding + SVM 的波动较小，但均值低于两个 fine-tuned encoders。本地 DeepSeek-7B 在所有语言上的主要限制仍是低 recall。

P3-single 只有一个 Rust fold，样本量为 60。正式迁移结论应使用 P3-multi macro-average，而不是引用 P3-single 的单次结果。

## 10. 哪些比较是公平的

### 可以直接进行

- 同一 trainable model 在 P0、P1、P2 上的描述性 protocol sensitivity；
- GraphCodeBERT、UniXcoder 和 embedding + SVM 在同一个 protocol/test split 上的比较；
- P3-multi 中相同 held-out folds 上的 per-language 与 macro-average 比较；
- DeepSeek-7B 与 DeepSeek-v4-flash 在完全相同 test files 上的 prompt-only预测比较。

### 需要限制性措辞

- Trainable encoders 与 zero-shot API model 的比较：前者使用 protocol train split，后者没有；
- P0 与 P1/P2 的因果解释：负样本构造也发生变化；
- P1 与 P2 的逐层泄露解释：P1 实际 problem overlap 也为 0；
- P3-single 与 P3-multi：fold 构造和训练随机性不完全相同；
- 早期 R1/R5 与 P0-P3：split 和 evaluation unit 不同。

## 11. 统计与复现状态

当前结果都是单次 point estimate，没有 3-5 个随机种子、bootstrap confidence interval 或 protocol-level significance test。因此目前可以报告“观察到明显下降/差异”，但不能报告“统计显著优于”。

### 11.1 11 类统计谬误扫描

- Simpson's paradox：已通过 P3 per-language 结果检查；不同语言存在差异，未仅依赖 aggregate。
- Ecological fallacy：未发现从语言均值直接推断单个程序行为的主张。
- Berkson/selection bias：数据来自筛选后的已准备样本，外部泛化范围有限，记为 CAUTION。
- Collider bias：当前分析没有协变量控制，不适用。
- Base-rate neglect：测试集被平衡，不能推断真实场景的 precision/PPV，记为 CAUTION。
- Regression to the mean：不适用。
- Survivorship bias：没有训练中途样本流失分析；对当前静态 benchmark 不构成主要问题。
- Look-elsewhere effect：运行了多个模型、协议和 prompt variant，但未做多重比较校正；只作描述性汇总，记为 CAUTION。
- Garden of forking paths：split 和 prompt 经多轮迭代后形成，未预注册，记为 CAUTION。
- Correlation versus causation：协议变化同时改变 leakage、problem partition 与负样本，不能作单因素因果陈述，记为 CAUTION。
- Reverse causality：不适用。

Fallacy scan coverage：`11/11`。

### 11.2 Reproducibility verdict

- Method：读取现存 structured outputs 与 runner scripts，未重新训练
- Verdict：`CANNOT_VERIFY`
- 原因：缺少多随机种子；GraphCodeBERT 指标为 restored metrics；API 模型可能随服务端版本更新；当前没有完整 environment lockfile 和统一 run manifest。

## 12. 结果文件索引

### AutoDL：P0-P3

```text
/root/autodl-tmp/graphcodebert_protocol_metrics_restored_20260622/{p0,p1,p2,p3}/metrics.json
/root/autodl-tmp/unixcoder_protocol_runs_20260622/{p0,p1,p2,p3}/metrics.json
/root/autodl-tmp/embedding_svm_protocol_runs_20260622/{p0,p1,p2,p3}/metrics.json
/root/autodl-tmp/deepseek_protocol_runs_20260622/{p0,p1,p2,p3}/metrics.json
/root/autodl-tmp/deepseek_api_flash_protocol_runs_20260623/{p0,p1,p2,p3}/metrics.json
```

### AutoDL：P3-multi

```text
/root/autodl-tmp/p3_multi_runs_graphcodebert_20260622/summary.json
/root/autodl-tmp/p3_multi_runs_unixcoder_20260622/summary.json
/root/autodl-tmp/p3_multi_runs_embedding_svm_20260623/summary.json
/root/autodl-tmp/p3_multi_runs_deepseek_20260623/summary.json
/root/autodl-tmp/p3_multi_runs_deepseek_api_flash_20260623/summary.json
```

### AutoDL：协议审计

```text
/root/autodl-tmp/clean_protocol_splits_v4/p0/audit.json
/root/autodl-tmp/clean_protocol_splits_v4/p1/audit.json
/root/autodl-tmp/clean_protocol_splits_v3/p2/audit.json
/root/autodl-tmp/clean_protocol_splits_v3/p3/audit.json
/root/autodl-tmp/p3_multi_splits_graphcodebert_20260622/heldout_*/audit.json
```

### 本地：早期 R1/R5

```text
outputs/r1_r5_summary_full_20260617_ckpt100.json
outputs/graphcodebert_r1_r5_summary_20260618.json
outputs/unixcoder_r1_r5_summary_20260618.json
outputs/embedding_svm_r1_r5_summary_20260618.json
outputs/deepseek_r1_qwen7b_r1_r5_summary_20260618.json
outputs/graphcodebert_leakage_audit.md
```

## 13. 后续主结果口径

论文或对外报告中建议采用以下层级：

1. 以 P0 audit 证明旧 pair-random protocol 存在 contamination；
2. 以 P2 作为主要 clean cross-problem benchmark；
3. 将当前 P1 称为“第二个 balanced clean partition/code-component split”，不要声称它只移除了 code leakage；
4. 以 P3-multi macro-F1 和跨语言标准差报告 unseen-language transfer；
5. 将 R1/R5 放入 preliminary study 或 protocol-motivation 小节，明确标记为 full-dataset、非独立测试结果；
6. 在进行多种子复跑和置信区间计算前，将当前模型差异称为 descriptive evidence，而不是 statistically significant superiority。
