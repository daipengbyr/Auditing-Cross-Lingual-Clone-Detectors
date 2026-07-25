#!/usr/bin/env bash
set -euo pipefail
cd /root/autodl-tmp/CLCCD-main
PYBIN=/root/miniconda3/bin/python
OUT=/root/autodl-tmp/phase5_embedding_svm_20260712
MODEL_DIR=/root/autodl-tmp/second_round_extensions_20260625/embedding_svm_p2/embedding_svm_train
mkdir -p "$OUT"/preserving "$OUT"/breaking_v1
$PYBIN predict_embedding_svm.py --input phase5_semantic_preserving_model_input.jsonl --output $OUT/preserving/predictions.json --model-dir $MODEL_DIR --batch-size 32 --max-length 256 > $OUT/preserving/run.stdout.log 2> $OUT/preserving/run.stderr.log
$PYBIN predict_embedding_svm.py --input phase5_semantic_breaking_model_input.jsonl --output $OUT/breaking_v1/predictions.json --model-dir $MODEL_DIR --batch-size 32 --max-length 256 > $OUT/breaking_v1/run.stdout.log 2> $OUT/breaking_v1/run.stderr.log
