# PaddleOCR-VL + vLLM — API Usage Guide

## Quick Start

```bash
# 1. Start the vLLM server
bash launch_server.sh

# 2. Verify it's running
curl http://localhost:8000/health

# 3. Run batch OCR
source /home/asiamath/Users/PJ/.venv_5090/bin/activate
python process_batch_v3.py
```

---

## 1. Server Launch

### launch_server.sh

```bash
bash launch_server.sh          # default port 8000
bash launch_server.sh 8118     # custom port
```

Starts a vLLM server hosting `PaddleOCR-VL-0.9B` with batch-optimized parameters:

| Parameter | Value | Description |
|---|---|---|
| `gpu-memory-utilization` | 0.9 | 90% VRAM allocated for KV cache |
| `max-model-len` | 16384 | Max token context per sequence |
| `max-num-seqs` | 256 | Max concurrent sequences batched per GPU step |
| `max-num-batched-tokens` | 16384 | Total token budget across all batched sequences |

### Manual launch (equivalent)

```bash
source /home/asiamath/.venv_vllm/bin/activate

uv run paddleocr genai_server \
  --model_name PaddleOCR-VL-0.9B \
  --backend vllm \
  --port 8000 \
  --backend_config <(cat <<'EOF'
gpu-memory-utilization: 0.9
max-model-len: 16384
max-num-seqs: 256
max-num-batched-tokens: 16384
trust-remote-code: true
EOF
)
```

### Health check

```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## 2. Batch Processing (process_batch_v3.py)

### Configuration

Edit the top of `process_batch_v3.py`:

```python
INPUT_ROOT  = "/path/to/input/pdfs"       # Recursive PDF scan
OUTPUT_ROOT = "/path/to/output/markdown"   # Mirrors input folder structure
VLLM_URL    = "http://localhost:8000/v1"   # vLLM server endpoint
VL_REC_MAX_CONCURRENCY = 16               # Concurrent requests to vLLM
```

### Run

```bash
source /home/asiamath/Users/PJ/.venv_5090/bin/activate
python process_batch_v3.py
```

### Features

- **Resume support** — skips files that already have non-empty `.md` output
- **PDF validation** — pre-checks PDF headers, skips corrupt files
- **Simplified → Traditional Chinese** conversion via `opencc`
- **Batch inference** — sends up to `VL_REC_MAX_CONCURRENCY` sub-image requests concurrently to vLLM

### Output

```
OUTPUT_ROOT/
├── _log_success.txt       # [HH:MM:SS] filename for each success
├── _log_error.txt         # [HH:MM:SS] filename -> error message
├── subfolder1/
│   ├── exam_paper_1.md
│   └── exam_paper_2.md
└── subfolder2/
    └── exam_paper_3.md
```

### Tuning VL_REC_MAX_CONCURRENCY

| Value | When to use |
|---|---|
| 8 | Low VRAM or small `max-num-seqs` on server |
| 16 | Default — good balance for RTX 5090 |
| 32–64 | If GPU utilization is still low (check `nvidia-smi`) |

Rule of thumb: increase until `nvidia-smi` shows ~80%+ GPU utilization, then stop.

---

## 3. Python API (Direct Usage)

### Single file OCR

```python
from paddleocr import PaddleOCRVL

pipeline = PaddleOCRVL(
    vl_rec_backend="vllm-server",
    vl_rec_server_url="http://localhost:8000/v1",
    vl_rec_max_concurrency=16,
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_chart_recognition=False,
)

for result in pipeline.predict("exam.pdf"):
    result.save_to_markdown(save_path="./output")
```

### Multiple files (list input)

```python
files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

for result in pipeline.predict(files):
    result.save_to_markdown(save_path="./output")
```

### Directory input

```python
for result in pipeline.predict("/path/to/pdf_folder/"):
    result.save_to_markdown(save_path="./output")
```

### Streaming with predict_iter

```python
# Memory-efficient — yields results one at a time
for result in pipeline.predict_iter("exam.pdf"):
    print(result.markdown)
```

### PaddleOCRVL constructor options

```python
PaddleOCRVL(
    # --- Backend ---
    vl_rec_backend="vllm-server",          # "vllm-server" | "native"
    vl_rec_server_url="http://...:8000/v1",
    vl_rec_max_concurrency=16,             # concurrent requests to vLLM

    # --- Pre-processing toggles ---
    use_doc_orientation_classify=False,     # auto-rotate detection
    use_doc_unwarping=False,               # dewarp curved documents
    use_chart_recognition=False,           # chart/table recognition

    # --- Layout detection ---
    layout_detection_model_name="PP-DocLayoutV2",  # default model
)
```

---

## 4. vLLM OpenAI-Compatible API

The vLLM server exposes an OpenAI-compatible chat completions endpoint. You can call it directly for custom integrations.

### Chat completion with image

```bash
# Base64 encode an image
IMG_B64=$(base64 -w0 exam_page.png)

curl -s http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"PaddleOCR-VL-0.9B\",
    \"messages\": [{
      \"role\": \"user\",
      \"content\": [
        {\"type\": \"text\", \"text\": \"Perform OCR on this image and return markdown.\"},
        {\"type\": \"image_url\", \"image_url\": {\"url\": \"data:image/png;base64,${IMG_B64}\"}}
      ]
    }],
    \"max_tokens\": 4096
  }"
```

### Python (via openai SDK)

```python
from openai import OpenAI
import base64

client = OpenAI(base_url="http://localhost:8000/v1", api_key="unused")

with open("exam_page.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

response = client.chat.completions.create(
    model="PaddleOCR-VL-0.9B",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Perform OCR on this image and return markdown."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
        ],
    }],
    max_tokens=4096,
)
print(response.choices[0].message.content)
```

---

## 5. FastAPI Service (Docker)

For containerized deployment, use the GPU Docker service.

### Build and run

```bash
cd /home/asiamath/Users/PJ/ocr_service_gpu

docker build -t ocr-vllm .

docker run -d --gpus all \
    --name ocr_gpu_service \
    -p 8118:8118 -p 8000:8000 \
    --shm-size=16g \
    -v ~/.paddlex:/root/.paddlex \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    ocr-vllm
```

### Endpoints

| Method | URL | Description |
|---|---|---|
| GET | `/health` | `{"status":"ok","pipeline_ready":true}` |
| GET | `/predict?image_path=/path/to/img.png` | Run OCR on a file inside the container |

### Example

```bash
# Copy an image into the container
docker cp exam.png ocr_gpu_service:/tmp/exam.png

# Run OCR
curl "http://localhost:8118/predict?image_path=/tmp/exam.png"
```

Response:
```json
{
  "status": "success",
  "filename": "exam.png",
  "elapsed_sec": 2.34,
  "results": ["# Exam Title\n\n1. Question one..."]
}
```

---

## 6. Web UIs

### Gradio visual interface

```bash
python /home/asiamath/Users/PJ/gradio_app.py
# http://localhost:7861
```

Upload images/PDFs, view side-by-side original + OCR result.

### Batch processing GUI

```bash
python /home/asiamath/Users/PJ/gui_batch.py
# http://localhost:9999  (login: asiamath / 123)
```

Concurrent batch processing with throughput metrics.

---

## 7. Troubleshooting

### Server won't start

```bash
# Check if port is already in use
lsof -i :8000

# Check GPU availability
nvidia-smi
```

### Batch processing is slow

1. Check GPU utilization: `watch -n1 nvidia-smi`
2. If GPU util < 50%, increase `VL_REC_MAX_CONCURRENCY` in the script
3. If GPU util is high but throughput is low, increase `max-num-batched-tokens` on the server

### Out of memory

Reduce server parameters:
```bash
bash launch_server.sh  # then edit:
# gpu-memory-utilization: 0.8  (down from 0.9)
# max-num-seqs: 128            (down from 256)
# max-model-len: 8192          (down from 16384)
```

### Corrupt PDF errors

`process_batch_v3.py` pre-validates PDF headers and logs skipped files to `_log_error.txt`. If a file passes validation but still fails, it will be caught and logged without crashing the batch.

### Resume after interruption

Just re-run `python process_batch_v3.py`. It automatically skips files that already have non-empty `.md` output.
