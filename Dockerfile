FROM --platform=$BUILDPLATFORM python:3.8-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM --platform=$TARGETPLATFORM python:3.8-slim

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.8/site-packages/ /usr/local/lib/python3.8/site-packages/

# Copy the application files
COPY main.py /app/

# Create log directory
RUN mkdir -p /app/logs

# Set the command
CMD ["python", "main.py"] 