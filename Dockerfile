# Base image with FFmpeg + CUDA pre-compiled
FROM jrottenberg/ffmpeg:6.1-nvidia as ffmpeg

# Minimal Python runtime
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

# Cache bust: Force rebuild when code changes
ARG CACHE_BUST=v2.1

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip curl && \
    rm -rf /var/lib/apt/lists/*

# Copy FFmpeg binaries from first stage
COPY --from=ffmpeg /usr/local/bin/ /usr/local/bin/
COPY --from=ffmpeg /usr/local/lib/ /usr/local/lib/

# Install Python dependencies
RUN pip3 install --no-cache-dir runpod requests

WORKDIR /workspace
COPY worker.py /workspace/worker.py

CMD ["python3", "/workspace/worker.py"]