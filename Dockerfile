FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# ✅ Geçmişte başarılı olan port strategy
ENV PORT=8001
ENV HOST=0.0.0.0
ENV PYTHONPATH=/app

# Expose port - environment'tan gelir
EXPOSE $PORT

# Health check - geçmişte çalışan method
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# ✅ Flexible startup - PORT env'den gelir
CMD uvicorn main:app --host $HOST --port $PORT --workers 1
