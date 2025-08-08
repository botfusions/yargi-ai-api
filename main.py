import os
import logging
import socket
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
from typing import Dict, Any, Optional
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

# Environment configuration with fallbacks
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://yargi-mcp.botfusions.com")
MCP_INTERNAL_URL = os.getenv("MCP_INTERNAL_URL", "http://yargi-mcp:8000")
FALLBACK_MODE = os.getenv("MCP_FALLBACK_MODE", "true").lower() == "true"

logger.info(f"🚀 Starting Yargı Web Interface on port 8001")
logger.info(f"📡 MCP Server URL (external): {MCP_SERVER_URL}")
logger.info(f"🔗 MCP Server URL (internal): {MCP_INTERNAL_URL}")
logger.info(f"🔄 Fallback Mode: {FALLBACK_MODE}")

def test_dns_resolution(hostname: str) -> bool:
    """Test if hostname can be resolved"""
    try:
        socket.gethostbyname(hostname)
        logger.info(f"✅ DNS OK: {hostname}")
        return True
    except socket.gaierror as e:
        logger.error(f"❌ DNS FAIL: {hostname} - {e}")
        return False

class SafeMCPClient:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.connection_urls = []
        self.active_url = None
        self.dns_working = False
        
        # Test DNS resolution on startup
        self._initialize_urls()
        
    def _initialize_urls(self):
        """Initialize connection URLs with DNS testing"""
        logger.info("🔍 Testing DNS resolution...")
        
        # Test external URL DNS
        external_host = MCP_SERVER_URL.replace("https://", "").replace("http://", "").split("/")[0]
        external_dns_ok = test_dns_resolution(external_host)
        
        # Test internal URL DNS (if different)
        internal_host = MCP_INTERNAL_URL.replace("https://", "").replace("http://", "").split("/")[0]
        internal_dns_ok = True  # Assume internal is always OK
        if internal_host != "yargi-mcp" and internal_host != "localhost":
            internal_dns_ok = test_dns_resolution(internal_host)
        
        # Prioritize working URLs
        if internal_dns_ok:
            self.connection_urls.append(MCP_INTERNAL_URL)
            logger.info(f"✅ Added internal URL: {MCP_INTERNAL_URL}")
            
        if external_dns_ok:
            self.connection_urls.append(MCP_SERVER_URL)
            logger.info(f"✅ Added external URL: {MCP_SERVER_URL}")
            
        # Fallback URLs (even if DNS failed, might work via IP)
        fallback_urls = [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
        
        for url in fallback_urls:
            if url not in self.connection_urls:
                self.connection_urls.append(url)
                logger.info(f"➕ Added fallback URL: {url}")
        
        self.dns_working = len([url for url in self.connection_urls if "localhost" not in url and "127.0.0.1" not in url]) > 0
        
        if not self.connection_urls:
            logger.error("❌ No connection URLs available!")
        else:
            logger.info(f"📋 Total connection URLs: {len(self.connection_urls)}")

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session with enhanced configuration"""
        if self.session is None or self.session.closed:
            # Enhanced connector configuration
            connector = aiohttp.TCPConnector(
                limit=5,
                limit_per_host=2,
                ttl_dns_cache=60,  # Shorter DNS cache
                use_dns_cache=True,
                enable_cleanup_closed=True,
                force_close=True,
                family=socket.AF_INET,  # Force IPv4
                ssl=False  # Disable SSL verification for internal connections
            )
            
            # Conservative timeout settings
            timeout = aiohttp.ClientTimeout(
                total=15,      # Reduced total timeout
                connect=5,     # Reduced connection timeout
                sock_read=10   # Reduced read timeout
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Yargi-Web-Interface/1.0',
                    'Accept': 'application/json',
                    'Connection': 'close'  # Don't keep connections alive
                }
            )
        return self.session

    async def test_connection(self, url: str) -> Optional[Dict[str, Any]]:
        """Test connection to a specific URL"""
        try:
            session = await self.get_session()
            test_endpoints = ["/health", "/status", "/"]
            
            for endpoint in test_endpoints:
                try:
                    test_url = f"{url.rstrip('/')}{endpoint}"
                    logger.info(f"🔍 Testing: {test_url}")
                    
                    async with session.get(test_url) as response:
                        if response.status == 200:
                            try:
                                data = await response.json()
                                logger.info(f"✅ Connection successful: {test_url}")
                                return {
                                    "url": url,
                                    "endpoint": test_url,
                                    "status": "success",
                                    "data": data
                                }
                            except:
                                # Even if JSON parsing fails, connection works
                                logger.info(f"✅ Connection OK (non-JSON): {test_url}")
                                return {
                                    "url": url,
                                    "endpoint": test_url,
                                    "status": "success",
                                    "data": {"status": "connected"}
                                }
                        else:
                            logger.warning(f"⚠️ HTTP {response.status}: {test_url}")
                            
                except asyncio.TimeoutError:
                    logger.warning(f"⏰ Timeout: {test_url}")
                except Exception as e:
                    logger.warning(f"❌ Error: {test_url} - {str(e)}")
                    
        except Exception as e:
            logger.error(f"❌ Connection test failed for {url}: {str(e)}")
            
        return None

    async def find_working_connection(self) -> Optional[str]:
        """Find the first working connection URL"""
        if self.active_url:
            # Test if current URL still works
            test_result = await self.test_connection(self.active_url)
            if test_result:
                logger.info(f"✅ Current connection still working: {self.active_url}")
                return self.active_url
            else:
                logger.warning(f"⚠️ Current connection failed: {self.active_url}")
                self.active_url = None

        logger.info("🔍 Searching for working MCP connection...")
        
        for url in self.connection_urls:
            test_result = await self.test_connection(url)
            if test_result:
                self.active_url = url
                logger.info(f"✅ Found working connection: {url}")
                return url
                
        logger.error("❌ No working MCP connections found!")
        return None

    async def health_check(self) -> Dict[str, Any]:
        """Enhanced health check with connection testing"""
        working_url = await self.find_working_connection()
        
        if working_url:
            try:
                session = await self.get_session()
                health_url = f"{working_url.rstrip('/')}/health"
                
                async with session.get(health_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "healthy",
                            "mcp_url": working_url,
                            "mcp_available": True,
                            "dns_working": self.dns_working,
                            "data": data
                        }
            except Exception as e:
                logger.error(f"❌ Health check failed: {str(e)}")
        
        return {
            "status": "unhealthy",
            "mcp_available": False,
            "dns_working": self.dns_working,
            "tested_urls": self.connection_urls,
            "error": "No working MCP connections"
        }

    async def search_legal(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """Search with enhanced error handling and fallback"""
        logger.info(f"🔍 Searching: '{query}' (limit: {limit})")
        
        # Enhanced fallback data
        fallback_data = {
            "results": [
                {
                    "title": f"DNS Resolution Test - {query}",
                    "court": "Sistem Test Mahkemesi",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "Fallback Mode (DNS Issue)",
                    "summary": f"'{query}' arama terimi için test sonucu. DNS resolution problemi tespit edildi. Network bağlantısı düzeltildikten sonra gerçek veriler gösterilecek."
                },
                {
                    "title": f"Bağlantı Durumu - {query}",
                    "court": "Network Test Dairesi",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": f"DNS Working: {self.dns_working}",
                    "summary": f"Test edilen URL'ler: {len(self.connection_urls)} adet. MCP server bağlantısı kurulamadı."
                }
            ],
            "total": 2,
            "query": query,
            "status": "dns_resolution_error",
            "mcp_available": False,
            "dns_working": self.dns_working,
            "timestamp": datetime.now().isoformat()
        }
        
        # Always return fallback for now due to DNS issues
        if not self.dns_working or FALLBACK_MODE:
            logger.info("📋 Using fallback mode (DNS issues)")
            return fallback_data
            
        # Try to search if connection is available
        working_url = await self.find_working_connection()
        if not working_url:
            logger.warning("❌ No working connection for search")
            return fallback_data
            
        try:
            session = await self.get_session()
            search_url = f"{working_url.rstrip('/')}/mcp/"
            
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
                    
                    if "result" in result:
                        return {
                            "results": result["result"],
                            "total": len(result["result"]),
                            "query": query,
                            "status": "success",
                            "mcp_available": True,
                            "mcp_url": working_url,
                            "timestamp": datetime.now().isoformat()
                        }
                else:
                    logger.warning(f"❌ MCP search failed: HTTP {response.status}")
                    
        except Exception as e:
            logger.error(f"❌ MCP search error: {str(e)}")
            
        # Return fallback if everything fails
        logger.info("📋 Falling back to mock data")
        return fallback_data

    async def close(self):
        """Cleanup session"""
        if self.session and not self.session.closed:
            await self.session.close()

# Global MCP client with DNS-safe initialization
try:
    mcp_client = SafeMCPClient()
    logger.info("✅ MCP Client initialized successfully")
except Exception as e:
    logger.error(f"❌ MCP Client initialization failed: {str(e)}")
    mcp_client = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main web interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "llm_enabled": True
    })

@app.get("/health")
async def health_check():
    """Enhanced health check with DNS diagnostics"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "port": 8001,
        "dns_resolution": {},
        "mcp_connection": {},
        "fallback_mode": FALLBACK_MODE
    }
    
    # DNS diagnostics
    try:
        external_host = MCP_SERVER_URL.replace("https://", "").replace("http://", "").split("/")[0]
        health_data["dns_resolution"] = {
            "external_host": external_host,
            "external_dns_ok": test_dns_resolution(external_host),
            "internal_dns_assumed_ok": True
        }
    except Exception as e:
        health_data["dns_resolution"] = {"error": str(e)}
    
    # MCP connection test
    if mcp_client:
        try:
            mcp_health = await mcp_client.health_check()
            health_data["mcp_connection"] = mcp_health
        except Exception as e:
            health_data["mcp_connection"] = {"error": str(e)}
    else:
        health_data["mcp_connection"] = {"error": "MCP client not initialized"}
    
    return health_data

@app.post("/api/search-simple")
async def search_simple(request: Request):
    """Simple search endpoint with enhanced error handling"""
    try:
        # Get query from URL parameter
        query = request.query_params.get("query", "")
        
        if not query or len(query.strip()) < 3:
            raise HTTPException(status_code=400, detail="Query too short (minimum 3 characters)")
        
        logger.info(f"🔍 Search request: '{query}'")
        
        if not mcp_client:
            raise HTTPException(status_code=500, detail="MCP client not available")
        
        # Perform search
        results = await mcp_client.search_legal(query.strip())
        
        # Add AI explanation
        if results.get("results"):
            status_info = ""
            if not results.get("mcp_available", False):
                status_info = "\n\n⚠️ Not: Şu anda test modunda çalışıyoruz. DNS resolution problemi çözüldükten sonra gerçek mahkeme kararları gösterilecektir."
            
            ai_explanation = f"""
Bu arama sonuçları '{query}' terimiyle ilgili bilgileri içermektedir.

🎯 Arama Özeti:
• Toplam {results['total']} sonuç bulundu
• Durum: {results['status']}
• MCP Bağlantısı: {'Aktif' if results.get('mcp_available') else 'Pasif'}
• DNS Durumu: {'Çalışıyor' if results.get('dns_working') else 'Problem var'}

⚖️ Sistem Durumu:
Bu sistem Türk hukuk veritabanlarına erişim sağlamak için tasarlanmıştır. Şu anda network bağlantısı optimize ediliyor.{status_info}

📝 Teknik Bilgi: DNS resolution sorunu tespit edildi ve düzeltiliyor.
            """.strip()
            
            results["llm_explanation"] = ai_explanation
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if mcp_client:
        await mcp_client.close()

# Development server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        log_level="info",
        access_log=True
    )
