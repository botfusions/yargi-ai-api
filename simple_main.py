"""
Turkish Legal AI API - Minimal Deployment Version
Simple FastAPI server without MCP dependencies for production deployment
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uvicorn

# FastAPI app
app = FastAPI(
    title="Turkish Legal AI API",
    description="""
    Turkish Legal Search API - Production Ready Version
    
    ## Features
    - Health monitoring endpoints
    - API status and information
    - Ready for MCP integration
    - CORS enabled for frontend integration
    
    ## Usage
    Navigate to `/docs` for interactive API documentation.
    """,
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Port configuration
PORT = int(os.getenv("PORT", 8001))
HOST = os.getenv("HOST", "0.0.0.0")

# Pydantic models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    environment: str
    port: int

class MevzuatSearchRequest(BaseModel):
    query: str = Field(..., description="Turkish search query")
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=10, ge=1, le=50, description="Results per page")

class MevzuatSearchResponse(BaseModel):
    query: str
    total_results: int
    page: int
    results: List[Dict[str, Any]]
    status: str

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Health check endpoint for the API service"""
    return HealthResponse(
        status="healthy",
        service="turkish-legal-ai-api",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        environment=os.getenv("ENVIRONMENT", "production"),
        port=PORT
    )

@app.get("/api/test", tags=["System"])
async def test_endpoint():
    """Test endpoint to verify API functionality"""
    return {
        "message": "Turkish Legal AI API is operational!",
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "port": PORT,
        "version": "1.0.0",
        "ready_for_mcp_integration": True
    }

@app.get("/api/info", tags=["System"])
async def api_info():
    """API information and status"""
    return {
        "api_name": "Turkish Legal AI API",
        "version": "1.0.0",
        "description": "Turkish Legal Search API - Production Ready",
        "status": "operational",
        "deployment": "successful",
        "features": [
            "Health monitoring",
            "CORS enabled",
            "Production ready",
            "MCP integration ready"
        ],
        "documentation": "/docs",
        "last_updated": datetime.now().isoformat()
    }

@app.post("/api/mevzuat/search", response_model=MevzuatSearchResponse, tags=["Mevzuat"])
async def search_mevzuat(request: MevzuatSearchRequest):
    """
    Search Turkish legislation - Mock endpoint ready for MCP integration
    """
    # Mock response - replace with actual MCP integration
    mock_results = [
        {
            "id": "1",
            "title": f"Mock result for: {request.query}",
            "type": "KANUN",
            "number": "5237",
            "date": "2004-09-26",
            "description": "This is a mock result. Real results will come from MCP integration."
        }
    ]
    
    return MevzuatSearchResponse(
        query=request.query,
        total_results=1,
        page=request.page,
        results=mock_results,
        status="success"
    )

@app.get("/api/mevzuat/popular", tags=["Mevzuat"])
async def get_popular_laws():
    """Get popular Turkish laws - Mock endpoint"""
    popular_laws = [
        {"id": "5237", "name": "Türk Ceza Kanunu", "type": "KANUN", "year": "2004"},
        {"id": "6102", "name": "Türk Borçlar Kanunu", "type": "KANUN", "year": "2011"},
        {"id": "4721", "name": "Türk Medeni Kanunu", "type": "KANUN", "year": "2001"},
        {"id": "213", "name": "Vergi Usul Kanunu", "type": "KANUN", "year": "1961"},
        {"id": "6698", "name": "Kişisel Verilerin Korunması Kanunu", "type": "KANUN", "year": "2016"}
    ]
    
    return {
        "status": "success",
        "message": "Popular Turkish laws retrieved successfully",
        "count": len(popular_laws),
        "laws": popular_laws,
        "note": "This is a mock response. Real data will come from MCP integration."
    }

@app.get("/api/mevzuat/test", tags=["Mevzuat"])
async def test_mevzuat():
    """Test mevzuat endpoints"""
    return {
        "status": "success",
        "message": "Mevzuat API endpoints are operational",
        "timestamp": datetime.now().isoformat(),
        "available_endpoints": [
            "POST /api/mevzuat/search",
            "GET /api/mevzuat/popular",
            "GET /api/mevzuat/test"
        ],
        "ready_for_mcp": True
    }

@app.get("/api/status", tags=["System"])
async def system_status():
    """Complete system status"""
    return {
        "service": "Turkish Legal AI API",
        "version": "1.0.0",
        "status": "operational",
        "uptime": "Ready for production",
        "endpoints": {
            "system": 4,
            "mevzuat": 3,
            "total": 7
        },
        "deployment": {
            "platform": "Docker",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "port": PORT,
            "host": HOST
        },
        "integrations": {
            "mcp_ready": True,
            "cors_enabled": True,
            "docs_available": True
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print(f"Starting Turkish Legal AI API on {HOST}:{PORT}")
    print(f"Documentation available at: http://{HOST}:{PORT}/docs")
    print(f"Health check at: http://{HOST}:{PORT}/health")
    
    uvicorn.run(
        "simple_main:app",
        host=HOST,
        port=PORT,
        reload=False,
        workers=1
    )