FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    dnsutils \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Manual install missing packages
RUN pip install aiohttp==3.9.1

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port 8001
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8001/health || exit 1

# Environment defaults
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8001
ENV LOG_LEVEL=info
ENV MCP_FALLBACK_MODE=true

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
