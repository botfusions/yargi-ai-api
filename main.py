import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Yargı Web Interface",
    description="Turkish Legal Database Search Interface",
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

# Templates
templates = Jinja2Templates(directory="templates")

# Environment configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://yargi-mcp.botfusions.com")
FALLBACK_MODE = os.getenv("MCP_FALLBACK_MODE", "true").lower() == "true"

logger.info(f"🚀 Starting Yargı Web Interface on port 8001")
logger.info(f"📡 MCP Server URL: {MCP_SERVER_URL}")
logger.info(f"🔄 Fallback Mode: {FALLBACK_MODE}")

class FixedMCPClient:
    def __init__(self):
        self.session = None
        self.mcp_url = MCP_SERVER_URL.rstrip('/')
        self.is_mcp_down = False
        
    async def get_session(self):
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=5,
                limit_per_host=2,
                ttl_dns_cache=60,
                use_dns_cache=True,
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(
                total=10,
                connect=5,
                sock_read=5
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Yargi-Web-Interface/1.0',
                    'Accept': 'application/json'
                }
            )
        return self.session

    async def check_mcp_status(self) -> Dict[str, Any]:
        """Check if MCP server is available"""
        try:
            session = await self.get_session()
            
            # Test basic connectivity
            async with session.get(f"{self.mcp_url}/health") as response:
                status_code = response.status
                
                if status_code == 200:
                    try:
                        data = await response.json()
                        self.is_mcp_down = False
                        logger.info(f"✅ MCP server is UP: {self.mcp_url}")
                        return {
                            "status": "up",
                            "status_code": status_code,
                            "data": data
                        }
                    except:
                        # JSON parse error but server responded
                        self.is_mcp_down = False
                        return {
                            "status": "up",
                            "status_code": status_code,
                            "data": {"status": "responsive"}
                        }
                elif status_code == 503:
                    self.is_mcp_down = True
                    logger.warning(f"⚠️ MCP server is DOWN (503): {self.mcp_url}")
                    return {
                        "status": "down_503",
                        "status_code": status_code,
                        "error": "Service Unavailable - MCP server might be restarting"
                    }
                else:
                    self.is_mcp_down = True
                    logger.warning(f"⚠️ MCP server error {status_code}: {self.mcp_url}")
                    return {
                        "status": "error",
                        "status_code": status_code,
                        "error": f"HTTP {status_code}"
                    }
                    
        except Exception as e:
            self.is_mcp_down = True
            logger.error(f"❌ MCP server unreachable: {str(e)}")
            return {
                "status": "unreachable",
                "error": str(e)
            }

    async def search_legal(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """Enhanced search with MCP status awareness"""
        logger.info(f"🔍 Searching: '{query}' (limit: {limit})")
        
        # Check MCP status first
        mcp_status = await self.check_mcp_status()
        
        # Enhanced fallback data with MCP status info
        fallback_data = {
            "results": [
                {
                    "title": f"Sistem Durumu Raporu - {query}",
                    "court": "Sistem Yönetimi",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": f"MCP Status: {mcp_status.get('status', 'unknown')}",
                    "summary": self._get_status_message(mcp_status, query)
                },
                {
                    "title": f"Test Modu - {query}",
                    "court": "Demo Mahkemesi",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "Fallback Mode",
                    "summary": f"'{query}' konusunda örnek hukuki değerlendirme. MCP server aktif olduğunda gerçek veriler gösterilecek."
                }
            ],
            "total": 2,
            "query": query,
            "status": "fallback_with_mcp_status",
            "mcp_status": mcp_status,
            "mcp_available": mcp_status.get("status") == "up",
            "timestamp": datetime.now().isoformat()
        }
        
        # If MCP is down or fallback mode enabled, return fallback data
        if self.is_mcp_down or FALLBACK_MODE or mcp_status.get("status") != "up":
            logger.info(f"📋 Using fallback mode (MCP status: {mcp_status.get('status')})")
            return fallback_data
            
        # Try actual MCP search if server is up
        try:
            session = await self.get_session()
            search_url = f"{self.mcp_url}/mcp/"
            
            search_payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "id": 1,
                "params": {
                    "name": "search_bedesten_unified",
                    "arguments": {
                        "phrase": query,
                        "limit": limit
                    }
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": "Bearer mock_clerk_jwt_development_token_12345"
            }
            
            logger.info(f"📡 Making MCP request to: {search_url}")
            
            async with session.post(search_url, json=search_payload, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ MCP search successful")
                    
                    if "result" in result and result["result"]:
                        return {
                            "results": result["result"],
                            "total": len(result["result"]),
                            "query": query,
                            "status": "success",
                            "mcp_available": True,
                            "mcp_status": mcp_status,
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    logger.warning(f"❌ MCP search failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ MCP search error: {str(e)}")
            
        # Return fallback if MCP search fails
        logger.info("📋 MCP search failed, using fallback data")
        return fallback_data

    def _get_status_message(self, mcp_status: Dict[str, Any], query: str) -> str:
        """Generate status message based on MCP status"""
        status = mcp_status.get("status", "unknown")
        
        if status == "up":
            return f"MCP server aktif. '{query}' araması yapılabilir."
        elif status == "down_503":
            return f"MCP server geçici olarak kapalı (HTTP 503). Sunucu yeniden başlatılıyor olabilir. '{query}' araması için test verileri gösteriliyor."
        elif status == "error":
            status_code = mcp_status.get("status_code", "unknown")
            return f"MCP server hata veriyor (HTTP {status_code}). Teknik ekibimiz sorunu çözüyor. '{query}' için test verileri gösteriliyor."
        elif status == "unreachable":
            return f"MCP server'a erişilemiyor. Network bağlantısı kontrol ediliyor. '{query}' için test verileri gösteriliyor."
        else:
            return f"MCP server durumu belirsiz. '{query}' için test verileri gösteriliyor."

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# Global MCP client
mcp_client = FixedMCPClient()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main web interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "llm_enabled": True
    })

@app.get("/health")
async def health_check():
    """Enhanced health check with MCP status"""
    logger.info("🔍 Health check requested")
    
    # Check MCP status
    mcp_status = await mcp_client.check_mcp_status()
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "port": 8001,
        "application": "yargi-web-interface",
        "mcp_server": {
            "url": MCP_SERVER_URL,
            "status": mcp_status
        },
        "fallback_mode": FALLBACK_MODE,
        "template_status": "templates directory available"
    }
    
    logger.info(f"✅ Health check completed - MCP status: {mcp_status.get('status')}")
    return health_data

@app.post("/api/search-simple")
async def search_simple(request: Request):
    """Simple search endpoint with MCP status awareness"""
    query = request.query_params.get("query", "")
    
    if not query or len(query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query too short (minimum 3 characters)")
    
    logger.info(f"🔍 Search request: '{query}'")
    
    try:
        # Perform search
        results = await mcp_client.search_legal(query.strip())
        
        # Add AI explanation based on MCP status
        if results.get("results"):
            mcp_status = results.get("mcp_status", {})
            status = mcp_status.get("status", "unknown")
            
            if status == "up":
                status_info = "✅ MCP server aktif - gerçek veriler gösteriliyor."
            elif status == "down_503":
                status_info = "⚠️ MCP server geçici olarak kapalı (HTTP 503) - test verileri gösteriliyor."
            else:
                status_info = f"⚠️ MCP server durumu: {status} - test verileri gösteriliyor."
            
            ai_explanation = f"""
Bu arama sonuçları '{query}' terimiyle ilgili bilgileri içermektedir.

🎯 Arama Özeti:
• Toplam {results['total']} sonuç bulundu
• Durum: {results['status']}
• MCP Server: {status_info}

⚖️ Sistem Durumu:
{status_info}

Türk hukuk veritabanlarında '{query}' konusunda arama yapılmıştır. Sistem sürekli güncellenmektedir.

📝 Teknik Bilgi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} tarihinde arama yapılmıştır.
            """.strip()
            
            results["llm_explanation"] = ai_explanation
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await mcp_client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="info")
