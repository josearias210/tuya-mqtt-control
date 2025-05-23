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
