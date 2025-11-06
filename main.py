import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI(
    title="Turkish Legal AI API",
    version="1.0.0",
    description="Simple Turkish Legal API - Ready to use!"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Turkish Legal AI API is running!",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "test": "/api/test",
            "search": "/api/search?query=YOUR_QUERY",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "turkish-legal-ai-api",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/test")
def test():
    return {
        "message": "API is working!",
        "status": "success",
        "platform": "Windows/Linux/Mac compatible"
    }

@app.get("/api/search")
def search(query: str = Query(..., description="Search query")):
    """
    Demo search endpoint
    Example: /api/search?query=iş hukuku
    """
    return {
        "query": query,
        "status": "success",
        "message": f"Searching for: {query}",
        "results": [
            {
                "title": f"Demo Result for '{query}'",
                "description": "This is a demo API. Connect to real legal databases for actual results.",
                "source": "Demo"
            }
        ],
        "note": "This is a demo API. Extend it with real legal data sources."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    print(f"\n🚀 Starting API on http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"✅ Health Check: http://localhost:{port}/health\n")
    uvicorn.run(app, host="0.0.0.0", port=port)