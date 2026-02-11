source .venv_vllm/bin/activate

uv run paddleocr genai_server \
  --model_name PaddleOCR-VL-0.9B \
  --backend vllm \
  --port 8118 \
  --backend_config <(echo -e 'gpu-memory-utilization: 0.9\nmax-model-len: 8192')