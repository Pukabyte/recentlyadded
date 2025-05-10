FROM python:3.8-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY main.py /app/

# Create log directory
RUN mkdir -p /app/logs

# Set the command
CMD ["python", "main.py"] 