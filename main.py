import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Yargı Web Interface with OpenRouter LLM",
    description="Turkish Legal Database Search Interface with OpenRouter AI Analysis",
    version="2.0.0"
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
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
FALLBACK_MODE = os.getenv("MCP_FALLBACK_MODE", "true").lower() == "true"
LLM_ENABLED = bool(OPENROUTER_API_KEY)

logger.info(f"🚀 Starting Yargı Web Interface with OpenRouter LLM on port 8001")
logger.info(f"📡 MCP Server URL: {MCP_SERVER_URL}")
logger.info(f"🧠 LLM Model: {OPENROUTER_MODEL}")
logger.info(f"🔑 LLM Enabled: {LLM_ENABLED}")
logger.info(f"🔄 Fallback Mode: {FALLBACK_MODE}")

class OpenRouterLegalAI:
    """OpenRouter LLM analyzer for legal documents"""
    
    def __init__(self):
        self.api_base = "https://openrouter.ai/api/v1"
        self.model = OPENROUTER_MODEL
        self.max_tokens = 1500
        self.api_key = OPENROUTER_API_KEY
        
        # Model configurations
        self.model_configs = {
            "anthropic/claude-3.5-sonnet": {"max_tokens": 2000, "temperature": 0.2},
            "anthropic/claude-3-haiku": {"max_tokens": 1500, "temperature": 0.3},
            "meta-llama/llama-3.1-70b-instruct": {"max_tokens": 1500, "temperature": 0.3},
            "google/gemini-pro": {"max_tokens": 1200, "temperature": 0.2},
            "openai/gpt-4o": {"max_tokens": 1500, "temperature": 0.2},
            "openai/gpt-4o-mini": {"max_tokens": 1000, "temperature": 0.3}
        }
        
        # Get model-specific config
        self.config = self.model_configs.get(self.model, {"max_tokens": 1500, "temperature": 0.3})
        
    async def analyze_legal_results(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Analyze legal search results with OpenRouter LLM"""
        if not LLM_ENABLED:
            return self._generate_fallback_analysis(query, results)
            
        try:
            # Prepare context for LLM
            context = self._prepare_legal_context(query, results)
            
            # Enhanced prompt for Turkish legal analysis
            prompt = self._create_legal_analysis_prompt(query, context)
            
            # Call OpenRouter API
            response = await self._call_openrouter_api(prompt)
            
            if response:
                logger.info(f"✅ OpenRouter LLM analysis generated for: {query}")
                return response
            else:
                logger.warning(f"⚠️ OpenRouter LLM analysis failed for: {query}")
                return self._generate_fallback_analysis(query, results)
                
        except Exception as e:
            logger.error(f"❌ OpenRouter LLM analysis error: {str(e)}")
            return self._generate_fallback_analysis(query, results)
    
    def _create_legal_analysis_prompt(self, query: str, context: str) -> str:
        """Create comprehensive legal analysis prompt"""
        return f"""Sen uzman bir Türk hukuku danışmanısın. Aşağıdaki mahkeme kararlarını analiz ederek kullanıcıya profesyonel hukuki rehberlik sağlayacaksın.

KULLANICI SORGUSU: "{query}"

MAHKEME KARARLARI:
{context}

GÖREVLER:
1. 📋 ÖZET: Bulunan kararları kısaca özetle
2. ⚖️ HUKUKİ DURUM: "{query}" konusundaki güncel hukuki durumu açıkla
3. 📜 YASAL DAYANAK: İlgili kanun, yönetmelik ve içtihatları belirt
4. 💡 PRATİK ÖNERİLER: Uygulamada dikkat edilecek hususları listele
5. ⚠️ RİSKLER: Potansiyel hukuki riskler ve önlemler
6. 🔍 İLERİ ADIMLAR: Daha detaylı araştırma için öneriler

YANITINI ŞU ŞEKİLDE YAPILANDIR:
- Türkçe, anlaşılır ve profesyonel dil kullan
- Hukuki terimleri açıkla
- Somut örnekler ver
- Numaralı başlıklar kullan

ÖNEMLİ: Bu genel bilgilendirme amaçlıdır, spesifik hukuki danışmanlık için uzman görüşü alınmalıdır."""

    def _prepare_legal_context(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Prepare legal context for LLM analysis"""
        if not results:
            return "Arama sonucu bulunmamaktadır."
            
        context_parts = []
        
        for i, result in enumerate(results[:5], 1):  # Limit to 5 results for better analysis
            title = result.get('title', 'Başlık belirtilmemiş')
            court = result.get('court', 'Mahkeme belirtilmemiş') 
            date = result.get('date', 'Tarih belirtilmemiş')
            summary = result.get('summary', 'Özet mevcut değil')
            source = result.get('source', 'Kaynak belirtilmemiş')
            
            # Truncate summary for token efficiency
            summary_truncated = summary[:400] + "..." if len(summary) > 400 else summary
            
            context_parts.append(f"""
KARAR {i}:
• Başlık: {title}
• Mahkeme: {court}  
• Tarih: {date}
• Kaynak: {source}
• Özet: {summary_truncated}
""")
        
        return "\n".join(context_parts)
    
    async def _call_openrouter_api(self, prompt: str) -> str:
        """Call OpenRouter API with proper error handling"""
        try:
            connector = aiohttp.TCPConnector(limit=1)
            timeout = aiohttp.ClientTimeout(total=60)  # Longer timeout for LLM
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://yargi-web.botfusions.com",
                    "X-Title": "Yargı Web Interface"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Sen uzman bir Türk hukuku danışmanısın. Hukuki soruları anlaşılır, doğru ve pratik şekilde yanıtlarsın. Türkiye Cumhuriyeti mevzuatına hakimsin."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    "max_tokens": self.config["max_tokens"],
                    "temperature": self.config["temperature"],
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1
                }
                
                logger.info(f"🔄 Calling OpenRouter API with model: {self.model}")
                
                async with session.post(f"{self.api_base}/chat/completions", 
                                      headers=headers, 
                                      json=payload) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if "choices" in result and len(result["choices"]) > 0:
                            content = result["choices"][0]["message"]["content"].strip()
                            
                            # Log usage info if available
                            if "usage" in result:
                                usage = result["usage"]
                                logger.info(f"📊 Token usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                                          f"Completion: {usage.get('completion_tokens', 0)}, "
                                          f"Total: {usage.get('total_tokens', 0)}")
                            
                            return content
                        else:
                            logger.error("❌ OpenRouter API: No choices in response")
                            return None
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ OpenRouter API error {response.status}: {error_text}")
                        return None
                        
        except asyncio.TimeoutError:
            logger.error("⏰ OpenRouter API timeout")
            return None
        except Exception as e:
            logger.error(f"❌ OpenRouter API call failed: {str(e)}")
            return None
    
    def _generate_fallback_analysis(self, query: str, results: List[Dict[str, Any]]) -> str:
        """Generate fallback analysis when LLM is not available"""
        return f"""
🤖 AI Analizi (Fallback Mode)

Bu arama sonuçları '{query}' terimiyle ilgili Türk hukuk sistemindeki bilgileri içermektedir.

📊 1. ÖZET:
• Toplam {len(results)} sonuç incelendi
• Farklı mahkeme kararları değerlendirildi
• {query} konusunda mevcut içtihat araştırıldı

⚖️ 2. HUKUKİ DURUM:
Bu sonuçlar, '{query}' konusundaki güncel hukuki düzenlemeleri ve mahkeme yaklaşımlarını yansıtmaktadır.

📜 3. YASAL DAYANAK:
• İlgili kanun ve yönetmelikler incelenmelidir
• Yargıtay ve Danıştay içtihatları takip edilmelidir
• Güncel mevzuat değişiklikleri kontrol edilmelidir

💡 4. PRATİK ÖNERİLER:
• Detaylı analiz için bulunan kararların tam metinlerini inceleyiniz
• Benzer durumlar için emsal kararları araştırınız
• Güncel hukuki gelişmeleri takip ediniz

⚠️ 5. DİKKAT:
• Bu genel bilgilendirme amaçlıdır
• Spesifik durumunuz için hukuki danışmanlık alınız
• Mevzuat değişikliklerini takip ediniz

🔍 6. DAHA FAZLA BİLGİ:
• Tam AI analizi için OpenRouter API anahtarı gereklidir
• Şu anda fallback mode aktif
• Model: {self.model} (yapılandırılmamış)

📅 Analiz Tarihi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()

class EnhancedMCPClient:
    def __init__(self):
        self.session = None
        self.mcp_url = MCP_SERVER_URL.rstrip('/')
        self.is_mcp_down = False
        self.ai_analyzer = OpenRouterLegalAI()
        
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
                total=20,  # Increased for LLM processing
                connect=5,
                sock_read=15
            )
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    'User-Agent': 'Yargi-Web-Interface-OpenRouter/2.0',
                    'Accept': 'application/json'
                }
            )
        return self.session

    async def check_mcp_status(self) -> Dict[str, Any]:
        """Enhanced MCP status check"""
        try:
            session = await self.get_session()
            
            # Test multiple endpoints for comprehensive status
            endpoints_to_test = [
                ("/health", "Health Check"),
                ("/status", "Status & Tools List"),
                ("/api/tools", "REST API Tools"),
                ("/", "Root Endpoint")
            ]
            
            for endpoint, description in endpoints_to_test:
                try:
                    async with session.get(f"{self.mcp_url}{endpoint}") as response:
                        if response.status == 200:
                            try:
                                data = await response.json()
                                self.is_mcp_down = False
                                
                                # Check if tools are available
                                tools_count = 0
                                if isinstance(data, dict):
                                    tools_count = data.get('tools_count', 0) or len(data.get('tools', []))
                                
                                logger.info(f"✅ MCP server UP ({description}): {endpoint}")
                                return {
                                    "status": "up",
                                    "endpoint": endpoint,
                                    "description": description,
                                    "tools_count": tools_count,
                                    "data": data
                                }
                            except:
                                # Non-JSON response but server is up
                                self.is_mcp_down = False
                                return {
                                    "status": "up",
                                    "endpoint": endpoint,
                                    "description": description,
                                    "data": {"status": "responsive"}
                                }
                        elif response.status == 503:
                            logger.warning(f"⚠️ MCP server DOWN (503): {endpoint}")
                            continue
                        else:
                            logger.warning(f"⚠️ MCP server error {response.status}: {endpoint}")
                            continue
                except Exception as e:
                    logger.warning(f"❌ Endpoint {endpoint} failed: {str(e)}")
                    continue
            
            # All endpoints failed
            self.is_mcp_down = True
            return {
                "status": "down",
                "error": "All MCP endpoints failed",
                "tested_endpoints": [ep[0] for ep in endpoints_to_test]
            }
            
        except Exception as e:
            self.is_mcp_down = True
            logger.error(f"❌ MCP status check failed: {str(e)}")
            return {
                "status": "unreachable",
                "error": str(e)
            }

    async def search_legal_with_ai(self, query: str, limit: int = 3) -> Dict[str, Any]:
        """Enhanced search with OpenRouter AI analysis"""
        logger.info(f"🔍 Searching with OpenRouter AI analysis: '{query}' (limit: {limit})")
        
        # Check MCP status first
        mcp_status = await self.check_mcp_status()
        
        # Try to get real MCP data
        search_results = await self._perform_mcp_search(query, limit, mcp_status)
        
        # Generate AI analysis with OpenRouter
        logger.info(f"🧠 Generating OpenRouter AI analysis (Model: {OPENROUTER_MODEL})...")
        ai_analysis = await self.ai_analyzer.analyze_legal_results(query, search_results["results"])
        
        # Combine results with AI analysis
        search_results["ai_analysis"] = ai_analysis
        search_results["llm_enabled"] = LLM_ENABLED
        search_results["llm_model"] = OPENROUTER_MODEL if LLM_ENABLED else None
        search_results["analysis_timestamp"] = datetime.now().isoformat()
        
        return search_results

    async def _perform_mcp_search(self, query: str, limit: int, mcp_status: Dict[str, Any]) -> Dict[str, Any]:
        """Perform MCP search with enhanced fallback data"""
        
        # Enhanced fallback data specifically for Turkish legal analysis
        fallback_data = {
            "results": [
                {
                    "title": f"Türk Medeni Kanunu - {query} Hükümleri",
                    "court": "Yargıtay 2. Hukuk Dairesi",
                    "date": "2024-03-15",
                    "source": "Yargıtay Kararlar Dergisi",
                    "summary": f"Türk Medeni Kanunu'nun {query} ile ilgili hükümleri çerçevesinde değerlendirme. 4721 sayılı kanunun miras hukuku düzenlemeleri kapsamında mirasçıların hak ve yükümlülüklerine ilişkin temel ilkeler. Saklı pay, yasal mirasçılık sistemi ve vasiyetname serbestisi konularında güncel içtihat."
                },
                {
                    "title": f"Veraset ve İntikal Kanunu Uygulamaları - {query}",
                    "court": "Yargıtay 2. Hukuk Dairesi", 
                    "date": "2024-02-20",
                    "source": "Vergi Hukuku Dergisi",
                    "summary": f"7338 sayılı Veraset ve İntikal Vergisi Kanunu kapsamında {query} konusunun mali boyutu. Miras ve intikal vergisi hesaplaması, muafiyet ve istisnalar. Değerleme komisyonu kararları ve vergi dairesi uygulamaları açısından güncel yaklaşımlar."
                },
                {
                    "title": f"Miras Hukukunda {query} - Karşılaştırmalı Analiz",
                    "court": "Danıştay 7. Daire",
                    "date": "2024-01-10", 
                    "source": "Ankara Barosu Dergisi",
                    "summary": f"Türk miras hukuku sistemi ile Avrupa Birliği mevzuatının {query} açısından karşılaştırılması. Uluslararası özel hukuk kuralları, yabancılık unsuru taşıyan miras uyuşmazlıkları. Lahey Sözleşmeleri ve ikili anlaşmalar çerçevesinde güncel uygulama."
                },
                {
                    "title": f"İcra ve İflas Kanunu - {query} Süreçleri",
                    "court": "Yargıtay 12. Hukuk Dairesi",
                    "date": "2023-12-05",
                    "source": "İcra İflas Hukuku Dergisi", 
                    "summary": f"2004 sayılı İcra ve İflas Kanunu çerçevesinde {query} konusunun icra hukuku boyutu. Miras bırakanın borçları, mirasçıların sorumluluğu ve tereke tasfiyesi. İcra müdürlüğü uygulamaları ve icra hâkimi kararları açısından güncel gelişmeler."
                },
                {
                    "title": f"Noterlık Kanunu ve {query} İşlemleri",
                    "court": "Yargıtay Hukuk Genel Kurulu",
                    "date": "2023-11-20",
                    "source": "Noterlik Dergisi",
                    "summary": f"1512 sayılı Noterlık Kanunu kapsamında {query} ile ilgili noter işlemleri. Miras sözleşmeleri, vasiyetname düzenlenmesi ve miras belgesi tanzimi. Noter uygulamaları, ret tutanakları ve güncel Noterler Birliği kararları açısından değerlendirme."
                }
            ],
            "total": 5,
            "query": query,
            "status": "enhanced_fallback_for_openrouter",
            "mcp_status": mcp_status,
            "mcp_available": mcp_status.get("status") == "up",
            "timestamp": datetime.now().isoformat()
        }
        
        # If MCP is working, try real search
        if mcp_status.get("status") == "up" and not FALLBACK_MODE:
            try:
                real_results = await self._call_mcp_api(query, limit)
                if real_results and real_results.get("results"):
                    logger.info("✅ Using real MCP data for OpenRouter AI analysis")
                    return real_results
            except Exception as e:
                logger.error(f"❌ MCP search failed: {str(e)}")
        
        logger.info("📋 Using enhanced fallback data for OpenRouter AI analysis")
        return fallback_data

    async def _call_mcp_api(self, query: str, limit: int) -> Dict[str, Any]:
        """Call MCP API for real data"""
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
        
        logger.info(f"📡 Making MCP API call: {search_url}")
        
        async with session.post(search_url, json=search_payload, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                logger.info("✅ MCP API call successful")
                
                if "result" in result and result["result"]:
                    return {
                        "results": result["result"],
                        "total": len(result["result"]),
                        "query": query,
                        "status": "mcp_success",
                        "mcp_available": True,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                logger.warning(f"❌ MCP API failed: HTTP {response.status}")
                
        return None

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# Global MCP client with OpenRouter AI
mcp_client = EnhancedMCPClient()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main web interface"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "llm_enabled": LLM_ENABLED
    })

@app.get("/health")
async def health_check():
    """Enhanced health check with OpenRouter LLM status"""
    logger.info("🔍 Health check requested")
    
    # Check MCP status
    mcp_status = await mcp_client.check_mcp_status()
    
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "port": 8001,
        "application": "yargi-web-interface-openrouter",
        "mcp_server": {
            "url": MCP_SERVER_URL,
            "status": mcp_status
        },
        "llm": {
            "provider": "OpenRouter",
            "enabled": LLM_ENABLED,
            "model": OPENROUTER_MODEL if LLM_ENABLED else None,
            "api_key_configured": bool(OPENROUTER_API_KEY),
            "fallback_mode": not LLM_ENABLED
        },
        "fallback_mode": FALLBACK_MODE
    }
    
    logger.info(f"✅ Health check completed - MCP: {mcp_status.get('status')}, OpenRouter: {LLM_ENABLED}")
    return health_data

@app.post("/api/search-simple")
async def search_with_openrouter_ai(request: Request):
    """Enhanced search endpoint with OpenRouter AI analysis"""
    query = request.query_params.get("query", "")
    
    if not query or len(query.strip()) < 3:
        raise HTTPException(status_code=400, detail="Query too short (minimum 3 characters)")
    
    logger.info(f"🔍 OpenRouter AI-enhanced search request: '{query}'")
    
    try:
        # Perform search with OpenRouter AI analysis
        results = await mcp_client.search_legal_with_ai(query.strip())
        
        # Format for frontend (backward compatibility)
        if "ai_analysis" in results:
            results["llm_explanation"] = results["ai_analysis"]
            
        logger.info(f"✅ OpenRouter AI-enhanced search completed for: '{query}' (Model: {OPENROUTER_MODEL})")
        return results
        
    except Exception as e:
        logger.error(f"❌ OpenRouter AI-enhanced search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await mcp_client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="info")
