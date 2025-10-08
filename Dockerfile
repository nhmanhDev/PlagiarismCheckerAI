# syntax=docker/dockerfile:1

# For GPU hosts, this base provides CUDA libs. On CPU-only hosts, runtime still works.
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
	PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
	python3 python3-pip python3-venv git curl ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency list first for better caching
COPY requirements.txt ./

# Install Python deps (Torch will detect CUDA runtime)
RUN pip3 install --no-cache-dir --upgrade pip \
	&& pip3 install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Expose default port
EXPOSE 8000

# Create a non-root user (optional)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Default start command (FastAPI + Uvicorn)
CMD ["python3", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
