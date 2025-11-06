import os
from fastapi import FastAPI, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

app = FastAPI(
    title="Turkish Legal AI API",
    version="1.0.0",
    description="Turkish Legal Search API with multiple endpoints"
)

# Pydantic Models
class SearchRequest(BaseModel):
    query: str
    court: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: Optional[int] = 10

class LegalAnalysisRequest(BaseModel):
    case_text: str
    analysis_type: Optional[str] = "general"

class CaseSearchRequest(BaseModel):
    case_number: str
    court: Optional[str] = None
    year: Optional[int] = None

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
            "health": "GET /health",
            "test": "GET /api/test",
            "search_get": "GET /api/search?query=YOUR_QUERY",
            "search_post": "POST /api/search",
            "courts": "GET /api/courts",
            "legal_analysis": "POST /api/legal-analysis",
            "case_search": "POST /api/case-search",
            "models": "GET /api/models",
            "docs": "GET /docs"
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
def search_get(query: str = Query(..., description="Search query")):
    """
    Demo search endpoint (GET method)
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

@app.post("/api/search")
def search_post(request: SearchRequest):
    """
    Advanced search endpoint (POST method)

    Example request body:
    {
        "query": "iş hukuku",
        "court": "Yargıtay",
        "date_from": "2020-01-01",
        "date_to": "2024-12-31",
        "limit": 10
    }
    """
    return {
        "query": request.query,
        "court": request.court,
        "date_range": {
            "from": request.date_from,
            "to": request.date_to
        },
        "status": "success",
        "message": f"Searching for: {request.query}",
        "results": [
            {
                "case_number": "2023/1234",
                "title": f"Demo Case: {request.query}",
                "court": request.court or "Yargıtay 9. Hukuk Dairesi",
                "date": "2023-05-15",
                "summary": "Bu bir demo sonuçtur. Gerçek veri tabanlarına bağlanarak gerçek sonuçlar alabilirsiniz.",
                "url": "https://example.com/case/2023-1234"
            },
            {
                "case_number": "2023/5678",
                "title": f"Demo Case 2: {request.query}",
                "court": request.court or "Yargıtay 22. Hukuk Dairesi",
                "date": "2023-08-20",
                "summary": "İkinci demo sonuç. API'yi genişleterek gerçek mahkeme veritabanlarından sonuç alabilirsiniz.",
                "url": "https://example.com/case/2023-5678"
            }
        ],
        "total": 2,
        "limit": request.limit,
        "note": "This is a demo API. Connect to real legal databases for actual results."
    }

@app.get("/api/courts")
def get_courts():
    """
    Get list of Turkish courts
    """
    return {
        "status": "success",
        "courts": [
            {"id": 1, "name": "Yargıtay", "type": "Temyiz", "departments": 23},
            {"id": 2, "name": "Danıştay", "type": "İdari Yargı", "departments": 15},
            {"id": 3, "name": "Anayasa Mahkemesi", "type": "Anayasa", "departments": 2},
            {"id": 4, "name": "Sayıştay", "type": "Mali Denetim", "departments": 8},
            {"id": 5, "name": "Bölge Adliye Mahkemeleri", "type": "İstinaf", "departments": 48},
            {"id": 6, "name": "Asliye Mahkemeleri", "type": "İlk Derece", "departments": 0},
            {"id": 7, "name": "Rekabet Kurumu", "type": "İdari", "departments": 1},
            {"id": 8, "name": "KVKK", "type": "İdari", "departments": 1}
        ],
        "total": 8
    }

@app.post("/api/legal-analysis")
def legal_analysis(request: LegalAnalysisRequest):
    """
    Analyze legal case text

    Example request body:
    {
        "case_text": "İşçi işveren arasında geçen uyuşmazlık...",
        "analysis_type": "labor_law"
    }
    """
    return {
        "status": "success",
        "analysis": {
            "case_type": request.analysis_type,
            "summary": f"Analiz: {request.case_text[:100]}...",
            "key_points": [
                "İşçi-İşveren İlişkisi",
                "İş Sözleşmesinin Feshi",
                "Tazminat Talebi"
            ],
            "relevant_laws": [
                "İş Kanunu Madde 17",
                "İş Kanunu Madde 18",
                "Borçlar Kanunu Madde 420"
            ],
            "precedents": [
                "Yargıtay 9. HD 2022/1234",
                "Yargıtay 22. HD 2021/5678"
            ],
            "recommendation": "Bu bir demo analizdir. AI model entegrasyonu ile detaylı hukuki analiz sağlanabilir."
        },
        "note": "This is a demo response. Connect to LLM for actual legal analysis."
    }

@app.post("/api/case-search")
def case_search(request: CaseSearchRequest):
    """
    Search for specific case by case number

    Example request body:
    {
        "case_number": "2023/1234",
        "court": "Yargıtay",
        "year": 2023
    }
    """
    return {
        "status": "success",
        "case": {
            "case_number": request.case_number,
            "court": request.court or "Yargıtay 9. Hukuk Dairesi",
            "year": request.year or 2023,
            "decision_date": "2023-05-15",
            "decision_number": "2023/5678",
            "parties": {
                "plaintiff": "Demo Davacı",
                "defendant": "Demo Davalı"
            },
            "subject": "İş Hukuku - Kıdem Tazminatı",
            "decision": "Davacı lehine karar verilmiştir.",
            "full_text_url": "https://example.com/cases/2023-1234"
        },
        "note": "This is a demo response. Connect to court databases for actual case data."
    }

@app.get("/api/models")
def get_models():
    """
    Get available AI models for legal analysis
    """
    return {
        "status": "success",
        "models": [
            {
                "id": "claude-3.5-sonnet",
                "name": "Claude 3.5 Sonnet",
                "provider": "Anthropic",
                "capability": "Advanced legal analysis",
                "cost": "$3.00/1M tokens"
            },
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "OpenAI",
                "capability": "General legal research",
                "cost": "$30/1M tokens"
            },
            {
                "id": "gemini-pro",
                "name": "Gemini Pro",
                "provider": "Google",
                "capability": "Multi-language legal analysis",
                "cost": "$1.25/1M tokens"
            }
        ],
        "total": 3,
        "note": "Connect to OpenRouter or direct APIs to use these models"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    print(f"\n🚀 Starting API on http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"✅ Health Check: http://localhost:{port}/health\n")
    uvicorn.run(app, host="0.0.0.0", port=port)