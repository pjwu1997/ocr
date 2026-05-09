#!/bin/bash
# ============================================================
# Launch PaddleOCR-VL-1.5 vLLM Server (batch-optimized for RTX 5090)
# ============================================================
#
# Model: PaddleOCR-VL-1.5-0.9B (SOTA 94.5% on OmniDocBench v1.5)
#
# Key parameters for batch throughput:
#   gpu-memory-utilization    : 0.9   — use 90% VRAM for KV cache
#   max-model-len             : 16384 — max context per sequence (model max)
#   max-num-seqs              : 256   — max concurrent sequences batched on GPU
#   max-num-batched-tokens    : 16384 — total token budget per batch step
#   enable-prefix-caching     : false — OCR tasks don't benefit from this
#   mm-processor-cache-gb     : 0     — no image reuse expected in OCR
#
# These let vLLM's continuous batching pack many concurrent OCR
# requests into a single GPU forward pass.
# ============================================================

set -euo pipefail

PORT="${1:-8000}"

echo "=== PaddleOCR-VL-1.5 vLLM Server ==="
echo "Port: ${PORT}"
echo "======================================"

source /home/asiamath/.venv_vllm/bin/activate

uv run paddleocr genai_server \
  --model_name PaddleOCR-VL-1.5-0.9B \
  --backend vllm \
  --port "${PORT}" \
  --backend_config <(cat <<'EOF'
gpu-memory-utilization: 0.9
max-model-len: 16384
max-num-seqs: 256
max-num-batched-tokens: 16384
enable-prefix-caching: false
mm-processor-cache-gb: 0
trust-remote-code: true
EOF
)
