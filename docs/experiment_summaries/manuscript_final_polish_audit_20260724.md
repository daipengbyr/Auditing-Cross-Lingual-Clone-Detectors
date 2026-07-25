# Final manuscript polish and consistency audit

**Reviewed source:** `/Users/daipeng/Documents/所有写的论文/els-cas-templates-2/cas-sc-sample.tex`  
**Review date:** 2026-07-24  
**Scope:** language, terminology, claim calibration, metric consistency, table/figure references, and LaTeX-facing checks. The manuscript source was **not modified**.

## Overall assessment

The manuscript now has a clear and credible argument: permissive evaluation can inflate apparent performance; clean partitions do not remove all shallow evidence; and semantic-preserving stability and semantic-breaking sensitivity are separate observable properties. The English is generally publication-ready. The remaining priority is not wholesale rewriting. It is to remove a small set of internal inconsistencies that a careful JSS reviewer would notice.

## Must fix before submission

### 1. Correct Table 2's protocol range and multirow spans

**Location:** lines 452 and 458--481.  
**Issue:** The caption says `P0--P3` and defines `P3-single`, but the table contains only P0, P1, and P2. Each `\multirow{4}{*}{...}` also spans four rows although only three protocol rows are present. This will cause visual misalignment and makes the table internally inconsistent.

**Recommended changes:**

- Change the caption to:
  ```latex
  \caption{Model performance under P0--P2.}
  ```
- Change every `\multirow{4}{*}{...}` in this table to `\multirow{3}{*}{...}`.
- Keep P3 analysis exclusively in the later P3-multi table, unless you intentionally reinsert the P3-single rows and explain why both P3 variants are shown.

### 2. Correct the column specification of the partner-shuffling table

**Location:** line 637.  
**Issue:** `\begin{tabular}{llcccccc}` declares eight columns, whereas the header and all rows contain six columns.

**Recommended replacement:**
```latex
\begin{tabular}{llcccc}
```

### 3. Reconcile the metric inventory with the metrics actually defined and reported

**Location:** lines 264, 346--385, 635--639.  
**Issue:** Line 264 lists `CPA, SSR, CDFR, preservation consistency, and breaking rejection rate`. CPA is not defined anywhere in the current methods or reported in a result table. SSR is defined but not reported in the current results. Conversely, OCA, SRR, ODC, and DCR are defined and/or reported but omitted from this summary. This makes the metric framework look unfinished.

**Recommended replacement for lines 264--265:**
```latex
Finally, we apply the same framework to GraphCodeBERT, UniXcoder, Embedding + SVM, DeepSeek-7B, DeepSeek-v4-flash, and Shallow Control. We report F1, balanced accuracy, and the area under the receiver operating characteristic curve (AUROC), where available. For behavioral audits, we report OCA, SRR, CDFR, PC, ODC, BRR, and DCR as applicable.
```

Then choose one consistent policy for SSR:

- **If SSR is not used in any table, figure, or appendix:** remove its definition in lines 348--356.
- **If it is a planned reported result:** add the corresponding result and state its role in Section 5.1.

Do not retain CPA unless its definition, formula, and result are restored.

### 4. Qualify the claim that every model used the same counterfactual pair sets

**Location:** line 279.  
**Issue:** The results do not report every audit for DeepSeek-7B. Therefore, “All models are evaluated on the same split files and counterfactual pair sets” overstates experimental coverage.

**Recommended replacement:**
```latex
All systems are evaluated on the same frozen split files. Where an audit is applicable and results are reported, models are evaluated on the same counterfactual pair sets.
```

### 5. Remove residual editing colour markup

**Locations:** lines 186, 250, 304, and 402.  
**Issue:** `\textcolor{blue}{...}` remains around ordinary figure/table references. It reads as tracked editing rather than final manuscript styling.

**Action:** remove `\textcolor{blue}{...}` and retain only the enclosed `Fig./Figure/Table~\ref{...}` text.

### 6. Fix three clear grammatical/typographic errors

| Location | Current text | Recommended text |
|---|---|---|
| Line 689 | `semantics-breaking changes` | `semantic-breaking changes` |
| Line 784 | `DeepSeek-v4-flash\ is` | `DeepSeek-v4-flash is` |
| Line 870 | `consequently, small differences` | `Consequently, small differences` |

### 7. Standardize protocol names and dash formatting

**Locations:** especially lines 274 and 412--416.  
**Issue:** The narrative calls P1/P2/P3 “code-disjoint”, “problem-disjoint”, and “held-out-language problem-disjoint”, but Table 1 switches to “Code-component clean”, “Problem-disjoint clean”, and “Held-out-language clean”. Also, `P0-P3` appears with a hyphen in line 274 rather than the manuscript's normal en dash.

**Recommended Table 1 protocol-name row:**

```latex
& Pair-random
& Code-disjoint
& Problem-disjoint
& Held-out-language problem-disjoint \\
```

Use `P0--P3` consistently in prose and captions. Keep `Code-hash component` as the *construction unit*, not as the protocol name.

### 8. Ensure the stated statistical analysis is actually delivered

**Location:** line 393.  
**Issue:** The methods promise bootstrap 95\% confidence intervals and Holm-corrected planned comparisons. No confidence intervals, p-values, comparison table, or supplement pointer appears in the current Results sections.

**Required decision:**

- **If these analyses have been computed:** add a compact statistical-results table or supplementary table, and cite it at the relevant RQ results.
- **If they have not been computed or will not be reported:** remove the bootstrap/Holm sentence rather than claiming an analysis that readers cannot inspect.

This is a scientific reporting issue, not a stylistic preference.

## Important precision and completeness improvements

### 9. Define AUROC in full at first use

**Location:** line 346.  
**Recommended replacement:**
```latex
When a detector returns continuous scores, we also report the area under the receiver operating characteristic curve (AUROC). AUROC is omitted for prompt-only settings that return only binary decisions.
```

### 10. Do not introduce an undefined “v1” intervention label

**Location:** line 773.  
**Issue:** `semantic-breaking v1 variants` is the only visible definition of `v1`; no `v2` is part of the main manuscript comparison.

**Recommended replacement:**
```latex
We therefore apply semantic-breaking variants to the same 94 positive P2 pairs.
```

If versioning matters for reproducibility, define `v1` in Methods and state why later variants are excluded from the primary analysis.

### 11. Use “cross-lingual” consistently in formal task descriptions

The manuscript's chosen formal term is **cross-lingual**. Replace the residual adjective `cross-language` in figure captions and prose with `cross-lingual` where it names the task or cases.

**Examples:**

- Line 309: `original cross-lingual code pair`
- Line 828: `Cross-lingual failure cases`
- Line 837: `these cross-lingual cases`
- Line 208: `cross-lingual clone detection`

`Java-to-X` and `target-language side` are already used consistently and should be retained.

### 12. Make the Phase 5 validation process reproducible enough for review

**Locations:** lines 319--323 and 696--713.  
**Issue:** The manuscript says transformations were checked “either automatically or through manual review”, but it does not state the acceptance criteria, what was automatically checked, how many reviewers performed manual checking, or how disagreements were handled. A reviewer will reasonably ask how semantic-preserving/breaking status was established.

**Add a short Methods paragraph specifying:**

- transformation templates and their eligibility conditions;
- automatic validation procedure, when applicable;
- manual-review protocol and reviewer count;
- exclusion criteria and retained counts;
- the explicit boundary that this is controlled mutation validation, not formal equivalence proof.

The existing threats-to-validity section gives the last boundary well; this addition makes the construction auditable.

### 13. Make the model/API version traceable

**Locations:** lines 290--294 and 861.  
**Issue:** DeepSeek-v4-flash is identified by a service-style name, but a reader needs the exact API model identifier, access date or fixed version, temperature/decoding configuration, and prompt variant used for each reported table. The current prose says these were frozen, but does not direct the reader to a reproducibility artifact.

**Action:** add a sentence in Methods or a Data/Code Availability statement that points to the frozen manifest/configuration repository. Confirm that `xu2026deepseek` is an official, stable reference for the actual model identifier rather than a placeholder or secondary citation.

## Recommended claim-calibration refinements

These are not factual errors. They improve precision and reduce avoidable reviewer pushback.

### 14. Bound the “no detector” statement to the evaluated counterfactual set

**Locations:** line 121, line 155, line 818, and line 874.  
**Risk:** “No detector reliably combines both properties” is broadly phrased, while the evidence comes from 94 selected positive P2 pairs and defined transformations.

**Preferred wording:**
```latex
No evaluated system achieved both high preserving stability and high breaking rejection on this counterfactual set.
```

This is stronger scientifically because its scope exactly matches the evidence.

### 15. Soften the causal attribution in the GraphCodeBERT interpretation

**Location:** lines 729 and 837.  
**Risk:** phrases such as “for the same reason” and “remains anchored in evidence” can sound like claims about internal representations, even though the discussion correctly states a behavioral boundary.

**Preferred wording:**
```latex
The result is consistent with a decision pattern that is insensitive to both edit types.
```

or

```latex
This behavioral pattern does not identify the evidence used internally by the model.
```

### 16. Avoid describing P1 and P2 as a strict ladder in the Results

**Location:** line 495 and nearby discussion.  
**Reason:** line 444 correctly explains that P1 and P2 are independently constructed clean partitions with only partial problem-set overlap. Maintain that nuance whenever P1/P2 score differences are described. The current wording is mostly good; keep `clean protocols` rather than implying that P2 is simply P1 plus one isolated control.

## Low-priority source and style cleanup

1. Remove the empty `flushleft` environment in lines 438--439.
2. Remove unused template acronym macros (`WGM`, `QE`, `EP`, `PMS`, `BEC`, and `DE`) in lines 44--51 if they are not used elsewhere.
3. Rename `fig:RQ2_result.pdf` to a semantic label such as `fig:shortcut_baselines_p2`, then update its sole reference. The current label is legal but unnecessarily file-like.
4. Use a non-file-like figure label consistently, e.g., `fig:shortcut_baselines_p2` rather than a label ending in `.pdf`.
5. Keep `\citep` and `\citet` conventions consistent. The manuscript is already close; the isolated `\cite{...}` usages in the baseline descriptions can be changed to `\citep{...}` if parenthetical citation style is intended.

## Verification status

- **Source review:** completed.
- **Reference labels / figures / tables:** manually audited in the source; no obvious unresolved reference was found during textual review.
- **Full LaTeX build:** not run because `latexmk` is unavailable in the current environment (`latexmk: command not found`). A final local compile is still necessary to catch overflow, float placement, bibliography warnings, and any class-specific errors.

## Suggested order of revision

1. Fix Table 2 and the partner-shuffling column specification.
2. Reconcile metrics and either report or remove the stated inferential statistics.
3. Remove blue markup and clear typos.
4. Add counterfactual validation/API traceability details.
5. Apply terminology and claim-calibration refinements.
6. Compile twice with BibTeX/Biber as required by the template, then inspect the PDF page by page.
