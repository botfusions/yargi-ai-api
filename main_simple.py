from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import os
from datetime import datetime

# Minimal FastAPI app
app = FastAPI(
    title="Turkish Legal AI API - Simple", 
    description="Minimal API for testing deployment",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Turkish Legal AI API is running!"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "turkish-legal-ai-api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/test")
async def test():
    return {
        "message": "API test successful!",
        "status": "working",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8001))
    HOST = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main_simple:app", host=HOST, port=PORT)