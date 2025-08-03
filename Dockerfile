# Use official FFmpeg image with CUDA support
FROM jrottenberg/ffmpeg:6.1-nvidia

# Cache bust: Force rebuild when code changes
ARG CACHE_BUST=v2.2

ENV DEBIAN_FRONTEND=noninteractive

# Install Python and required dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Verify FFmpeg installation and show info
RUN ffmpeg -version && \
    ffmpeg -encoders | grep nvenc && \
    echo "FFmpeg with CUDA support verified!"

# Install Python dependencies
RUN pip3 install --no-cache-dir runpod requests

# Create workspace directory
WORKDIR /workspace

# Copy worker script
COPY worker.py /workspace/worker.py

# Make sure FFmpeg is in PATH and executable
ENV PATH="/usr/local/bin:$PATH"

# Final verification that FFmpeg works
RUN which ffmpeg && ffmpeg -version

CMD ["python3", "/workspace/worker.py"]