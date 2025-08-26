FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY main.py .

# Expose port
EXPOSE 8001

# Simple start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]