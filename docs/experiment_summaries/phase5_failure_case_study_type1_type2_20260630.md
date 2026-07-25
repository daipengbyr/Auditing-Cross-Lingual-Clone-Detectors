# Phase 5 Failure Case Study (Type 1 + Type 2, 2026-06-30)

## Scope

This note implements the two highest-value failure-case directions for Phase 5:

1. `GraphCodeBERT` preserving succeeds but breaking fails.
2. `DeepSeek-v4-flash` preserving fails but breaking succeeds.

To make the contrast sharper, the cases below are chosen from the intersection where the same `source_pair_id` exhibits both patterns simultaneously. For `DeepSeek`, the prompt variant used here is `evidence_guided`, because it provides the strongest semantic-breaking sensitivity in the current Phase 5 result set.

`A4-full` is included as an auxiliary anchor, because it behaves like a shallow lexical/surface baseline and helps interpret whether the breaking mutation destroys shallow cues.

## Selection Rule

A case enters this sheet only if all conditions hold:

- `GraphCodeBERT`: original = `yes`, preserving = `yes`, breaking = `yes`
- `DeepSeek-v4-flash evidence_guided`: original = `yes`, preserving = `no`, breaking = `no`

This produces a clean opposition:

- encoder/shallow models keep the clone decision under both perturbations
- the API model rejects both, including the semantically preserving one

## Summary Table

| Case | Source pair | Lang-B | Problem | Preserving edit | Breaking edit | GraphCodeBERT | A4-full | DeepSeek-EG |
|---|---|---|---|---|---|---|---|---|
| C1 | `4a338c0ee00e93ff` | Python | `p02852` | identifier rename | boolean literal flip | preserve `yes`, break `yes` | preserve `yes`, break `yes` | preserve `no`, break `no` |
| C2 | `d581815418c7e597` | C++ | `p02612` | identifier rename | comparator flip | preserve `yes`, break `yes` | preserve `yes`, break `yes` | preserve `no`, break `no` |
| C3 | `14c63a8170301676` | Go | `p03206` | identifier rename | comparator flip | preserve `yes`, break `yes` | preserve `yes`, break `yes` | preserve `no`, break `no` |
| C4 | `250ba66423b35229` | JavaScript | `p02823` | identifier rename | comparator flip | preserve `yes`, break `yes` | preserve `yes`, break `yes` | preserve `no`, break `no` |

## Case C1: Python / `p02852`

### Model outcomes

- `GraphCodeBERT`: preserving `yes`; breaking `yes` (`prob_yes = 0.9808`)
- `A4-full`: preserving `yes`; breaking `yes` (`prob_yes = 0.5469`)
- `DeepSeek-v4-flash evidence_guided`: preserving `no`; breaking `no`

### Preserving edit

The preserving mutation is a pure identifier rename inside `codeB`:

```python
-    sap = s.append
+    renamed_var_1 = s.append
-        sl = len(s)
-        xap = x.append
+        renamed_var_2 = len(s)
+        renamed_var_3 = x.append
-                xap(s.pop(-1))
+                renamed_var_3(s.pop(-1))
```

### Breaking edit

The breaking mutation flips loop reachability:

```python
-    while True:
+    while False:
```

### Interpretation

This is an especially clean case. The semantics-breaking edit is drastic: the loop body becomes unreachable. Yet `GraphCodeBERT` and `A4-full` both keep the clone label. `DeepSeek` detects the breaking mutation, but it also rejects the preserving rename variant, showing semantic sensitivity with over-conservatism.

## Case C2: C++ / `p02612`

### Model outcomes

- `GraphCodeBERT`: preserving `yes`; breaking `yes` (`prob_yes = 0.9883`)
- `A4-full`: preserving `yes`; breaking `yes` (`prob_yes = 0.9099`)
- `DeepSeek-v4-flash evidence_guided`: preserving `no`; breaking `no`

### Preserving edit

Only the local variable name changes:

```cpp
-    int n;
-    cin>>n;
+    int renamedVar1;
+    cin>>renamedVar1;
...
-    else if(n<1000)
+    else if(renamedVar1<1000)
```

### Breaking edit

The mutation flips the first equality test:

```cpp
-    if(n==1000 ||n==2000 || n==3000 || ...)
+    if(n!=1000 ||n==2000 || n==3000 || ...)
```

### Interpretation

The mutated condition changes program behavior for a critical branch, but the surface form remains almost identical. This is exactly where shallow or holistic similarity can dominate. The fact that `A4-full` and `GraphCodeBERT` both retain `yes`, while `DeepSeek` flips to `no`, makes this a strong exemplar for the main Phase 5 contrast.

## Case C3: Go / `p03206`

### Model outcomes

- `GraphCodeBERT`: preserving `yes`; breaking `yes` (`prob_yes = 0.9875`)
- `A4-full`: preserving `yes`; breaking `yes` (`prob_yes = 0.8937`)
- `DeepSeek-v4-flash evidence_guided`: preserving `no`; breaking `no`

### Preserving edit

The preserving mutation renames scanner-related locals:

```go
-func StrStdin() (stringInput string) {
-	scanner := bufio.NewScanner(os.Stdin)
+func StrStdin() (renamedVar2 string) {
+	renamedVar1 := bufio.NewScanner(os.Stdin)
-	scanner.Scan()
-	stringInput = scanner.Text()
+	renamedVar1.Scan()
+	renamedVar2 = renamedVar1.Text()
```

### Breaking edit

A single comparison is inverted:

```go
-	if D == 22 {
+	if D != 22 {
```

### Interpretation

This case is useful because the breaking mutation is tiny in edit distance but large in semantics. `GraphCodeBERT` and `A4-full` appear insensitive to the functional effect of the branch inversion, while `DeepSeek` again rejects both the real breaking variant and the harmless rename variant.

## Case C4: JavaScript / `p02823`

### Model outcomes

- `GraphCodeBERT`: preserving `yes`; breaking `yes` (`prob_yes = 0.9832`)
- `A4-full`: preserving `yes`; breaking `yes` (`prob_yes = 0.7401`)
- `DeepSeek-v4-flash evidence_guided`: preserving `no`; breaking `no`

### Preserving edit

The preserving mutation renames I/O helper variables:

```javascript
-var lines = [];
-var reader = require('readline').createInterface({
+var renamedVar1 = [];
+var renamedVar2 = require('readline').createInterface({
-reader.on('line', (line) => {
-  lines.push(line);
+renamedVar2.on('line', (line) => {
+  renamedVar1.push(line);
```

### Breaking edit

The parity check is inverted:

```javascript
-    if(abs(a,b)%2n==0n) return abs(a,b)/2n;
+    if(abs(a,b)%2n!=0n) return abs(a,b)/2n;
```

### Interpretation

This case shows the same pattern outside Python/C++/Go. The branch condition is semantically critical, but high lexical overlap remains. Again, `GraphCodeBERT` and `A4-full` keep the clone judgment, whereas `DeepSeek` rejects both variants.

## Cross-Case Pattern

Across all four languages, the same qualitative pattern repeats:

- `GraphCodeBERT` is stable under preserving edits, but that stability extends into breaking cases where the prediction should ideally flip.
- `A4-full` behaves similarly, which strengthens the interpretation that the retained clone judgment is compatible with shallow lexical/structural matching.
- `DeepSeek-v4-flash evidence_guided` is semantically more sensitive, but the cost is lower preserving stability: it rejects even harmless rename-only variants.

## How To Use In The Paper

The cleanest use is as a short `Failure Case Study` subsection after the main Phase 5 tables:

1. Show one compact summary table with these four cases.
2. Expand one Python case and one non-Python case as two mini-figures or code boxes.
3. State the mechanism-level takeaway conservatively:

> On the same source pairs, GraphCodeBERT and A4-full frequently retain the clone decision after semantics-breaking edits, while DeepSeek-v4-flash is more likely to reject the breaking variant but can also over-reject semantics-preserving renamings.

## Source Files

- [GraphCodeBERT unified rows](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260628/phase5_unified_graphcodebert_phase5b)
- [A4-full unified rows](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260630/phase5_unified_a4_full_phase5b)
- [DeepSeek preserving rows (`evidence_guided`)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_preserving_pilot_20260627/preserving_metrics_deepseek_v4_flash_evidence_guided/semantic_preserving_pair_rows.csv)
- [DeepSeek breaking rows (`evidence_guided`)](/Users/daipeng/Documents/Codex/2026-06-15/files-mentioned-by-the-user-ws/outputs/third_round_phase5_unified_results_20260630/phase5_unified_deepseek_v4_flash_breaking_v1_evidence_guided/breaking_pair_rows.csv)
