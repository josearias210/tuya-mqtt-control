FROM python:3.11-slim

WORKDIR /app

# Install build tools and libffi headers
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libffi-dev \
      python3-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script and set entrypoint
COPY src/tuya_control.py .
CMD ["python", "tuya_control.py"]

LABEL org.opencontainers.image.title="tuya-mqtt-control"
LABEL org.opencontainers.image.description="A simple Python service to control Tuya Smart Bulbs via MQTT. Multi-arch Docker image for x64 and Raspberry Pi 5 (arm64)."
LABEL org.opencontainers.image.authors="Antonio Arias <https://programemos.net>"
LABEL org.opencontainers.image.licenses="MIT"
ARG VERSION=latest
LABEL org.opencontainers.image.version="${VERSION}"