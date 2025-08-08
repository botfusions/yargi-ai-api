import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from typing import Optional

# ✅ Minimal FastAPI app - hiçbir external dependency yok
app = FastAPI(
    title="Yargı AI API", 
    description="Turkish Legal Search API - Minimal Version",
    version="1.0.0"
)

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

@app.get("/health")
async def health():
    """
    Sadece environment variables - hiçbir external call yok
    """
    return {
        "status": "healthy",
        "service": "yargi-ai-api-minimal",
        "port": PORT,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0-minimal"
    }

@app.get("/")
async def root():
    return {
        "service": "Yargı AI API",
        "status": "running",
        "version": "minimal",
        "port": PORT,
        "docs": "/docs",
        "available_endpoints": [
            "/health",
            "/api/test",
            "/api/search",
            "/api/info"
        ]
    }

@app.get("/api/test")
async def test():
    """
    Basit test endpoint
    """
    return {
        "message": "API çalışıyor!",
        "status": "success",
        "timestamp": "2025-08-08",
        "port": PORT
    }

@app.get("/api/info")
async def info():
    """
    API bilgileri
    """
    return {
        "api_name": "Yargı AI API",
        "version": "1.0.0-minimal",
        "description": "Turkish Legal Search API",
        "features": [
            "Legal search",
            "AI analysis", 
            "Turkish law database access"
        ],
        "status": "operational"
    }

@app.post("/api/search")
async def search(
    query: str = Query(..., description="Arama sorgusu"),
    detailed: bool = Query(False, description="Detaylı analiz")
):
    """
    Mock legal search - external API calls olmadan
    """
    # Mock legal data
    mock_results = [
        {
            "title": f"Yargıtay Kararı - {query}",
            "court": "Yargıtay 9. Hukuk Dairesi",
            "date": "2024-11-15",
            "summary": f"{query} konusunda Yargıtay'ın güncel içtihatları ve değerlendirmeleri.",
            "relevance": "yüksek",
            "source": "yargitay"
        },
        {
            "title": f"Danıştay Görüşü - {query}",
            "court": "Danıştay 5. Daire", 
            "date": "2024-10-22",
            "summary": f"{query} ile ilgili idari hukuk perspektifinden analiz ve değerlendirmeler.",
            "relevance": "orta",
            "source": "danistay"
        },
        {
            "title": f"Hukuki Çerçeve - {query}",
            "court": "Mevzuat Analizi",
            "date": "2024-12-01", 
            "summary": f"{query} konusunda ilgili yasal düzenlemeler ve mevzuat hükümleri.",
            "relevance": "temel",
            "source": "mevzuat"
        }
    ]
    
    # Mock AI analysis
    ai_analysis = f"""Hukuki Değerlendirme - {query}

{query} konusunda Türk hukuk sistemi kapsamında şu noktalar değerlendirilmelidir:

1. **Yasal Çerçeve**
   - İlgili kanun ve yönetmelik hükümleri
   - Mevzuattaki tanımlar ve düzenlemeler

2. **Mahkeme İçtihatları**
   - Yargıtay kararları ve istikrarlı içtihat
   - Danıştay görüşleri ve idari yaklaşım

3. **Pratik Uygulamalar**
   - Hukuki süreçler ve gereklilikler
   - Uygulamada karşılaşılan durumlar

4. **Öneriler**
   - Güncel mevzuat takibi
   - Uzman hukuki danışmanlık
   - Belgesel hazırlık

{'Detaylı analiz ve örnek vakalar dikkate alınmalıdır.' if detailed else 'Bu genel bir değerlendirmedir.'}

**Not**: Spesifik durumunuz için mutlaka hukuk uzmanına başvurunuz."""

    return {
        "query": query,
        "results": mock_results,
        "ai_analysis": ai_analysis,
        "result_count": len(mock_results),
        "detailed_analysis": detailed,
        "status": "success",
        "mode": "mock_data",
        "timestamp": "2025-08-08"
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