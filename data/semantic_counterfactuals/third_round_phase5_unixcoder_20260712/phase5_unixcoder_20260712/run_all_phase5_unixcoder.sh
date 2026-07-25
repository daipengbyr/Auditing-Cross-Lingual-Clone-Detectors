#!/usr/bin/env bash
set -euo pipefail
cd /root/autodl-tmp/CLCCD-main
PYBIN=/root/miniconda3/bin/python
if [ ! -x "$PYBIN" ]; then PYBIN=python; fi
OUT=/root/autodl-tmp/phase5_unixcoder_20260712
MODEL=/root/autodl-tmp/second_round_extensions_20260625/unixcoder_p2/unixcoder_train/model
mkdir -p "$OUT"/preserving "$OUT"/breaking_v1 "$OUT"/breaking_v2_mini
$PYBIN predict_unixcoder_trunc.py --input phase5_semantic_preserving_model_input.jsonl --output $OUT/preserving/predictions.json --model $MODEL --model-family unixcoder --batch-size 32 --max-length 256 > $OUT/preserving/run.stdout.log 2> $OUT/preserving/run.stderr.log
$PYBIN predict_unixcoder_trunc.py --input phase5_semantic_breaking_model_input.jsonl --output $OUT/breaking_v1/predictions.json --model $MODEL --model-family unixcoder --batch-size 32 --max-length 256 > $OUT/breaking_v1/run.stdout.log 2> $OUT/breaking_v1/run.stderr.log
$PYBIN predict_unixcoder_trunc.py --input phase5_semantic_breaking_v2_model_input.jsonl --output $OUT/breaking_v2_mini/predictions.json --model $MODEL --model-family unixcoder --batch-size 32 --max-length 256 > $OUT/breaking_v2_mini/run.stdout.log 2> $OUT/breaking_v2_mini/run.stderr.log
