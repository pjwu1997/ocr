# AsiaMath OCR

PaddleOCR-VL-1.5 pipeline with a Gradio web UI and batch processing script.

## Architecture

- **vLLM server** — serves the PaddleOCR-VL-1.5-0.9B model on port 8000
- **Gradio app** — web UI on port 7860 for uploading PDF/images and viewing OCR results
- **Batch script** (`process_batch_v4.py`) — bulk OCR a directory of files

## Prerequisites

- NVIDIA GPU with driver installed
- `nvidia-container-toolkit` installed
- Docker + Docker Compose
- Python venv at `/home/asiamath/.venv_vllm` with all dependencies (paddleocr, vllm, gradio, opencc, pypdfium2, etc.)

## Docker Setup (auto-restart on reboot)

### Base image choice

Uses `nvidia/cuda:12.8.0-runtime-ubuntu22.04` because:
- Includes CUDA runtime libs (`libcudart.so` etc.) needed by PaddlePaddle
- `nvidia-container-toolkit` mounts the host GPU driver into the container
- The host Python venv (with torch cu128, vllm, paddleocr) is bind-mounted at `/venv`
- Alternatives considered:
  - `python:3.12-slim` — lighter but may miss CUDA runtime libs that PaddlePaddle expects
  - `nvidia/cuda:12.8.0-base-ubuntu22.04` — minimal, only driver compat stubs (~200MB smaller)

### Start

```bash
docker compose up -d
```

This starts both services with `restart: unless-stopped` — they auto-restart on server reboot or crash.

- vLLM server starts first (takes ~2 min to load the model)
- Gradio app waits for the server healthcheck to pass before starting
- Healthcheck: `curl http://localhost:8000/v1/models` every 30s, up to 10 retries with 120s start period

### Stop

```bash
docker compose down
```

### View logs

```bash
docker compose logs -f            # both services
docker compose logs -f vllm-server # server only
docker compose logs -f gradio-app  # app only
```

### Access

- Gradio UI: http://localhost:7860 (login: `admin` / `123`)
- vLLM API: http://localhost:8000/v1

## Manual Setup (without Docker)

### 1. Start vLLM backend

```bash
bash launch_server.sh
```

### 2. Start Gradio frontend

```bash
source /home/asiamath/.venv_vllm/bin/activate
python app.py
```

### 3. Batch processing (alternative to UI)

```bash
source /home/asiamath/.venv_vllm/bin/activate
python process_batch_v4.py
```

Processes files in the configured `INPUT_ROOT` directory, outputs markdown + segmented images to `OUTPUT_ROOT`. Supports resume (skips already-processed files).
