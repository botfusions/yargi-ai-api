import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import uvicorn
from typing import Optional
from datetime import datetime

# Import MCP endpoint routers
from yargi_endpoints import router as yargi_router
from mevzuat_endpoints import router as mevzuat_router

# Import error handlers
from error_handlers import setup_error_handlers

# Enhanced FastAPI app with MCP tools integration
app = FastAPI(
    title="Turkish Legal AI API - Complete", 
    description="""
    Comprehensive Turkish Legal Search API with 41+ tools integrated from yargi-mcp and mevzuat-mcp servers.
    
    ## Features
    - **38 Yargi-MCP tools**: Turkish courts, decisions, and legal databases
    - **3 Mevzuat-MCP tools**: Turkish legislation and regulations
    - **REST API endpoints**: All MCP tools exposed as standard REST endpoints
    - **Multiple courts supported**: Yargıtay, Danıştay, Anayasa Mahkemesi, KİK, Rekabet Kurumu, Sayıştay, KVKK, BDDK
    - **Advanced search capabilities**: Full-text search, filtering, pagination
    - **Document retrieval**: Markdown-formatted legal documents
    
    ## Court Systems Covered
    - Yargıtay (Supreme Court of Appeals) - 52 chambers/boards
    - Danıştay (Council of State) - 27 chambers/boards
    - Anayasa Mahkemesi (Constitutional Court) - Individual applications & norm control
    - Uyuşmazlık Mahkemesi (Jurisdictional Disputes Court)
    - KİK (Public Procurement Authority)
    - Rekabet Kurumu (Competition Authority) 
    - Sayıştay (Court of Accounts) - 8 chambers
    - KVKK (Personal Data Protection Authority)
    - BDDK (Banking Regulation and Supervision Agency)
    - Turkish Legislation Database (mevzuat.gov.tr)
    
    ## Usage
    Navigate to `/docs` for interactive API documentation or use the endpoints directly.
    """,
    version="2.0.0",
    contact={
        "name": "Turkish Legal AI API Support",
        "url": "https://github.com/turkish-legal-ai",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Include MCP endpoint routers
app.include_router(yargi_router)
app.include_router(mevzuat_router)

# Setup error handlers and middleware
setup_error_handlers(app)

# CORS
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

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["System"])
async def health():
    """
    Health check endpoint for the API service
    """
    return {
        "status": "healthy",
        "service": "turkish-legal-ai-api-complete",
        "port": PORT,
        "environment": os.getenv("ENVIRONMENT", "production"),
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "mcp_integration": {
            "yargi_mcp_tools": 38,
            "mevzuat_mcp_tools": 3,
            "total_tools": 41
        },
        "features": [
            "Turkish court decisions search",
            "Constitutional Court decisions",
            "Turkish legislation database",
            "Public procurement decisions",
            "Competition authority decisions",
            "Data protection decisions",
            "Banking regulation decisions",
            "Court of accounts decisions"
        ]
    }

@app.get("/api/info", tags=["System"])
async def api_info():
    """
    Complete API information and available endpoints
    """
    return {
        "api_name": "Turkish Legal AI API - Complete",
        "version": "2.0.0",
        "description": "Comprehensive Turkish Legal Search API with 41+ MCP tools",
        "total_endpoints": 50,
        "mcp_integration": {
            "yargi_mcp": {
                "tools": 38,
                "endpoints": 21,
                "courts": [
                    "Yargıtay (Supreme Court)",
                    "Danıştay (Council of State)",
                    "Anayasa Mahkemesi (Constitutional Court)",
                    "Uyuşmazlık Mahkemesi (Jurisdictional Disputes Court)",
                    "KİK (Public Procurement Authority)",
                    "Rekabet Kurumu (Competition Authority)",
                    "Sayıştay (Court of Accounts)",
                    "KVKK (Personal Data Protection Authority)",
                    "BDDK (Banking Regulation Agency)"
                ]
            },
            "mevzuat_mcp": {
                "tools": 3,
                "endpoints": 9,
                "database": "Turkish Legislation (mevzuat.gov.tr)",
                "coverage": "All Turkish laws and regulations"
            }
        },
        "key_features": [
            "Real-time court decision search",
            "Full-text legislation search", 
            "Document retrieval in Markdown",
            "Advanced filtering and pagination",
            "Multi-court unified search",
            "Constitutional Court individual applications",
            "Administrative and civil law decisions",
            "Regulatory authority decisions"
        ],
        "documentation": "/docs",
        "status": "operational",
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/test", tags=["System"])
async def test_endpoint():
    """
    Test endpoint to verify API functionality
    """
    return {
        "message": "Turkish Legal AI API is operational!",
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "port": PORT,
        "version": "2.0.0",
        "mcp_tools_available": 41,
        "endpoints": {
            "yargi_endpoints": 21,
            "mevzuat_endpoints": 9,
            "system_endpoints": 3
        },
        "test_urls": {
            "health_check": f"http://localhost:{PORT}/health",
            "api_documentation": f"http://localhost:{PORT}/docs",
            "yargi_tools": f"http://localhost:{PORT}/api/yargi/tools",
            "mevzuat_tools": f"http://localhost:{PORT}/api/mevzuat/tools",
            "server_health": f"http://localhost:{PORT}/api/yargi/health"
        }
    }

@app.get("/api/overview", tags=["System"])
async def api_overview():
    """
    Complete API overview with all available endpoints and tools
    """
    return {
        "service": "Turkish Legal AI API - Complete",
        "version": "2.0.0",
        "description": "Comprehensive REST API exposing 41+ Turkish legal database tools",
        "total_mcp_tools": 41,
        "total_rest_endpoints": 33,
        
        "yargi_mcp_integration": {
            "tools": 38,
            "endpoints": 21,
            "categories": {
                "bedesten_unified": "Multi-court search (Yargıtay, Danıştay, Local, Appeals)",
                "emsal": "Precedent decisions database", 
                "anayasa": "Constitutional Court (norm control + individual applications)",
                "uyusmazlik": "Jurisdictional disputes court",
                "kik": "Public procurement authority decisions",
                "rekabet": "Competition authority decisions",
                "sayistay": "Court of accounts decisions",
                "kvkk": "Personal data protection authority",
                "bddk": "Banking regulation and supervision agency"
            }
        },
        
        "mevzuat_mcp_integration": {
            "tools": 3,
            "endpoints": 9,
            "database": "mevzuat.gov.tr - Turkish Legislation Database",
            "features": [
                "Legislation search by name/number",
                "Full-text content search",
                "Article-level content retrieval",
                "Hierarchical structure navigation"
            ]
        },
        
        "key_endpoints": {
            "health_monitoring": "/health",
            "api_documentation": "/docs", 
            "yargi_health": "/api/yargi/health",
            "multi_court_search": "/api/yargi/bedesten/search",
            "constitutional_court": "/api/yargi/anayasa/search",
            "legislation_search": "/api/mevzuat/search",
            "popular_laws": "/api/mevzuat/popular"
        },
        
        "supported_formats": ["JSON", "Markdown"],
        "search_capabilities": [
            "Multi-court unified search",
            "Advanced filtering by date/type/chamber",
            "Full-text content search",
            "Pagination support",
            "Document retrieval with formatting"
        ],
        
        "deployment_ready": True,
        "cors_enabled": True,
        "documentation_available": True
    }

# ✅ Minimal startup - hiçbir network call YOK
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=HOST, 
        port=PORT, 
        reload=False,
        workers=1
    )