#!/bin/bash
# ============================================================
# Launch PaddleOCR-VL vLLM Server (batch-optimized for RTX 5090)
# ============================================================
#
# Key parameters for batch throughput:
#   gpu-memory-utilization : 0.9  — use 90% VRAM for KV cache
#   max-model-len         : 16384 — max context per sequence
#   max-num-seqs          : 256   — max concurrent sequences batched on GPU
#   max-num-batched-tokens: 16384 — total token budget per batch step
#
# These let vLLM's continuous batching pack many concurrent OCR
# requests into a single GPU forward pass.
# ============================================================

set -euo pipefail

PORT="${1:-8000}"

echo "=== PaddleOCR-VL vLLM Server ==="
echo "Port: ${PORT}"
echo "================================"

source /home/asiamath/.venv_vllm/bin/activate

uv run paddleocr genai_server \
  --model_name PaddleOCR-VL-0.9B \
  --backend vllm \
  --port "${PORT}" \
  --backend_config <(cat <<'EOF'
gpu-memory-utilization: 0.9
max-model-len: 16384
max-num-seqs: 256
max-num-batched-tokens: 16384
trust-remote-code: true
EOF
)
