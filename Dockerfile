FROM python:3.8-slim

WORKDIR /app

# Install dependencies and cron
RUN apt-get update && \
    apt-get install -y --no-install-recommends cron && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY main.py /app/
COPY entrypoint.sh /app/

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 