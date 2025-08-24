"""
Yargi-MCP REST API Endpoints
Exposes 38+ Turkish legal database tools as REST endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import subprocess
import json
import tempfile
import os

router = APIRouter(prefix="/api/yargi", tags=["Yargi MCP Tools"])

# Pydantic models for request/response validation
class HealthResponse(BaseModel):
    overall_status: str
    healthy_servers: int
    total_servers: int
    servers: Dict[str, Dict[str, Any]]
    check_timestamp: str

class SearchBedestenRequest(BaseModel):
    phrase: str = Field(..., description="Turkish search query")
    court_types: List[str] = Field(default=["YARGITAYKARARI", "DANISTAYKARAR"], description="Court types to search")
    birimAdi: str = Field(default="ALL", description="Chamber filter")
    kararTarihiStart: str = Field(default="", description="Start date (ISO 8601)")
    kararTarihiEnd: str = Field(default="", description="End date (ISO 8601)")
    pageNumber: int = Field(default=1, ge=1, description="Page number")

class SearchEmsalRequest(BaseModel):
    keyword: str = Field(default="", description="Keyword to search")
    start_date: str = Field(default="", description="Start date (DD.MM.YYYY)")
    end_date: str = Field(default="", description="End date (DD.MM.YYYY)")
    page_number: int = Field(default=1, ge=1, description="Page number")
    selected_regional_civil_chambers: List[str] = Field(default=[], description="Selected chambers")
    sort_criteria: str = Field(default="1", description="Sort criteria")
    sort_direction: str = Field(default="desc", description="Sort direction")

class SearchAnayasaRequest(BaseModel):
    decision_type: str = Field(..., description="Decision type: norm_denetimi or bireysel_basvuru")
    keywords: List[str] = Field(default=[], description="Keywords to search")
    keywords_all: List[str] = Field(default=[], description="All keywords must be present")
    keywords_any: List[str] = Field(default=[], description="Any of these keywords")
    page_to_fetch: int = Field(default=1, ge=1, le=100, description="Page to fetch")
    decision_start_date: str = Field(default="", description="Decision start date")
    decision_end_date: str = Field(default="", description="Decision end date")
    application_date_start: str = Field(default="", description="Application start date")
    application_date_end: str = Field(default="", description="Application end date")
    subject_category: str = Field(default="", description="Subject category")
    norm_type: str = Field(default="ALL", description="Norm type")
    decision_type_norm: str = Field(default="ALL", description="Decision type for norm")

class SearchUyusmazlikRequest(BaseModel):
    bolum: str = Field(default="ALL", description="Department selection")
    esas_yil: str = Field(default="", description="Case year")
    esas_sayisi: str = Field(default="", description="Case number")
    karar_yil: str = Field(default="", description="Decision year")
    karar_sayisi: str = Field(default="", description="Decision number")
    karar_date_begin: str = Field(default="", description="Decision start date")
    karar_date_end: str = Field(default="", description="Decision end date")
    icerik: str = Field(default="", description="Content search")
    hepsi: str = Field(default="", description="All words search")
    herhangi_birisi: str = Field(default="", description="Any words search")
    tumce: str = Field(default="", description="Exact phrase search")
    wild_card: str = Field(default="", description="Wildcard search")
    not_hepsi: str = Field(default="", description="Exclude words")
    uyusmazlik_turu: str = Field(default="ALL", description="Dispute type")
    karar_sonuclari: List[str] = Field(default=[], description="Decision results")
    kanun_no: str = Field(default="", description="Law number")
    resmi_gazete_date: str = Field(default="", description="Official Gazette date")
    resmi_gazete_sayi: str = Field(default="", description="Official Gazette number")

class SearchKikRequest(BaseModel):
    karar_tipi: str = Field(default="rbUyusmazlik", description="Decision type")
    karar_no: str = Field(default="", description="Decision number")
    yil: str = Field(default="", description="Year")
    karar_tarihi_baslangic: str = Field(default="", description="Start date")
    karar_tarihi_bitis: str = Field(default="", description="End date")
    karar_metni: str = Field(default="", description="Decision text search")
    basvuru_sahibi: str = Field(default="", description="Applicant")
    ihaleyi_yapan_idare: str = Field(default="", description="Procuring entity")
    basvuru_konusu_ihale: str = Field(default="", description="Tender subject")
    resmi_gazete_tarihi: str = Field(default="", description="Official Gazette date")
    resmi_gazete_sayisi: str = Field(default="", description="Official Gazette number")
    page: int = Field(default=1, ge=1, description="Page number")

class SearchRekabetRequest(BaseModel):
    KararTuru: str = Field(default="ALL", description="Decision type")
    KararSayisi: str = Field(default="", description="Decision number")
    KararTarihi: str = Field(default="", description="Decision date")
    YayinlanmaTarihi: str = Field(default="", description="Publication date")
    sayfaAdi: str = Field(default="", description="Page title search")
    PdfText: str = Field(default="", description="PDF text search")
    page: int = Field(default=1, ge=1, description="Page number")

class SearchSayistayRequest(BaseModel):
    decision_type: str = Field(..., description="Decision type: genel_kurul, temyiz_kurulu, or daire")
    karar_tarih_baslangic: str = Field(default="", description="Start date (DD.MM.YYYY)")
    karar_tarih_bitis: str = Field(default="", description="End date (DD.MM.YYYY)")
    karar_no: str = Field(default="", description="Decision number")
    karar_ek: str = Field(default="", description="Decision appendix")
    karar_tamami: str = Field(default="", description="Full text search")
    web_karar_konusu: str = Field(default="ALL", description="Decision subject")
    web_karar_metni: str = Field(default="", description="Decision text")
    kamu_idaresi_turu: str = Field(default="ALL", description="Public administration type")
    dosya_no: str = Field(default="", description="File number")
    temyiz_karar: str = Field(default="", description="Appeals decision text")
    temyiz_tutanak_no: str = Field(default="", description="Appeals meeting minutes number")
    yili: str = Field(default="", description="Year (YYYY)")
    hesap_yili: str = Field(default="", description="Account year")
    ilam_no: str = Field(default="", description="Audit report number")
    ilam_dairesi: str = Field(default="ALL", description="Audit chamber")
    yargilama_dairesi: str = Field(default="ALL", description="Chamber selection")
    start: int = Field(default=0, ge=0, description="Starting record")
    length: int = Field(default=10, ge=1, le=100, description="Records per page")

class SearchKvkkRequest(BaseModel):
    keywords: str = Field(..., description="Search keywords")
    page: int = Field(default=1, ge=1, le=50, description="Page number")

class SearchBddkRequest(BaseModel):
    keywords: str = Field(..., description="Search keywords")
    page: int = Field(default=1, ge=1, description="Page number")

# Helper function to call MCP tools
async def call_mcp_tool(tool_name: str, parameters: dict) -> dict:
    """Call MCP tool via command line interface"""
    try:
        # Create temporary file with parameters
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(parameters, f)
            temp_file = f.name
        
        # Call the MCP tool
        cmd = ["python", "-c", f"""
import sys
import json
sys.path.append('.')

# Import the specific MCP function based on tool name
tool_map = {{
    'check_government_servers_health': 'from mcp__yargi_mcp__check_government_servers_health import mcp__yargi_mcp__check_government_servers_health as tool_func',
    'search_bedesten_unified': 'from mcp__yargi_mcp__search_bedesten_unified import mcp__yargi_mcp__search_bedesten_unified as tool_func',
    'get_bedesten_document_markdown': 'from mcp__yargi_mcp__get_bedesten_document_markdown import mcp__yargi_mcp__get_bedesten_document_markdown as tool_func',
    'search_emsal_detailed_decisions': 'from mcp__yargi_mcp__search_emsal_detailed_decisions import mcp__yargi_mcp__search_emsal_detailed_decisions as tool_func',
    'get_emsal_document_markdown': 'from mcp__yargi_mcp__get_emsal_document_markdown import mcp__yargi_mcp__get_emsal_document_markdown as tool_func',
    'search_anayasa_unified': 'from mcp__yargi_mcp__search_anayasa_unified import mcp__yargi_mcp__search_anayasa_unified as tool_func',
    'get_anayasa_document_unified': 'from mcp__yargi_mcp__get_anayasa_document_unified import mcp__yargi_mcp__get_anayasa_document_unified as tool_func',
    'search_uyusmazlik_decisions': 'from mcp__yargi_mcp__search_uyusmazlik_decisions import mcp__yargi_mcp__search_uyusmazlik_decisions as tool_func',
    'get_uyusmazlik_document_markdown_from_url': 'from mcp__yargi_mcp__get_uyusmazlik_document_markdown_from_url import mcp__yargi_mcp__get_uyusmazlik_document_markdown_from_url as tool_func',
    'search_kik_decisions': 'from mcp__yargi_mcp__search_kik_decisions import mcp__yargi_mcp__search_kik_decisions as tool_func',
    'get_kik_document_markdown': 'from mcp__yargi_mcp__get_kik_document_markdown import mcp__yargi_mcp__get_kik_document_markdown as tool_func',
    'search_rekabet_kurumu_decisions': 'from mcp__yargi_mcp__search_rekabet_kurumu_decisions import mcp__yargi_mcp__search_rekabet_kurumu_decisions as tool_func',
    'get_rekabet_kurumu_document': 'from mcp__yargi_mcp__get_rekabet_kurumu_document import mcp__yargi_mcp__get_rekabet_kurumu_document as tool_func',
    'search_sayistay_unified': 'from mcp__yargi_mcp__search_sayistay_unified import mcp__yargi_mcp__search_sayistay_unified as tool_func',
    'get_sayistay_document_unified': 'from mcp__yargi_mcp__get_sayistay_document_unified import mcp__yargi_mcp__get_sayistay_document_unified as tool_func',
    'search_kvkk_decisions': 'from mcp__yargi_mcp__search_kvkk_decisions import mcp__yargi_mcp__search_kvkk_decisions as tool_func',
    'get_kvkk_document_markdown': 'from mcp__yargi_mcp__get_kvkk_document_markdown import mcp__yargi_mcp__get_kvkk_document_markdown as tool_func',
    'search_bddk_decisions': 'from mcp__yargi_mcp__search_bddk_decisions import mcp__yargi_mcp__search_bddk_decisions as tool_func',
    'get_bddk_document_markdown': 'from mcp__yargi_mcp__get_bddk_document_markdown import mcp__yargi_mcp__get_bddk_document_markdown as tool_func',
}}

# Load parameters
with open('{temp_file}', 'r', encoding='utf-8') as f:
    params = json.load(f)

# Execute the function
exec(tool_map.get('{tool_name}', 'raise ValueError("Unknown tool")'))
result = tool_func(**params)
print(json.dumps(result, ensure_ascii=False, indent=2))
"""]
        
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        # Clean up temp file
        os.unlink(temp_file)
        
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"MCP tool error: {result.stderr}")
        
        return json.loads(result.stdout)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calling MCP tool: {str(e)}")

# HEALTH CHECK ENDPOINTS
@router.get("/health", response_model=HealthResponse, summary="Check Government Servers Health")
async def check_servers_health():
    """Check if Turkish government legal database servers are operational"""
    return await call_mcp_tool("check_government_servers_health", {})

# BEDESTEN UNIFIED SEARCH (Yargıtay, Danıştay, Local Courts, Appeals Courts, KYB)
@router.post("/bedesten/search", summary="Search Multiple Turkish Courts")
async def search_bedesten_unified(request: SearchBedestenRequest):
    """Search multiple Turkish courts (Yargıtay, Danıştay, Local Courts, Appeals Courts, KYB)"""
    return await call_mcp_tool("search_bedesten_unified", request.dict())

@router.get("/bedesten/document/{document_id}", summary="Get Bedesten Document")
async def get_bedesten_document(document_id: str):
    """Get legal decision document from Bedesten API in Markdown format"""
    return await call_mcp_tool("get_bedesten_document_markdown", {"documentId": document_id})

# EMSAL PRECEDENT DECISIONS
@router.post("/emsal/search", summary="Search Emsal Precedent Decisions")
async def search_emsal_decisions(request: SearchEmsalRequest):
    """Search Emsal precedent decisions with detailed criteria"""
    return await call_mcp_tool("search_emsal_detailed_decisions", request.dict())

@router.get("/emsal/document/{document_id}", summary="Get Emsal Document")
async def get_emsal_document(document_id: str):
    """Get Emsal precedent decision text in Markdown format"""
    return await call_mcp_tool("get_emsal_document_markdown", {"id": document_id})

# CONSTITUTIONAL COURT (ANAYASA MAHKEMESİ)
@router.post("/anayasa/search", summary="Search Constitutional Court Decisions")
async def search_anayasa_unified(request: SearchAnayasaRequest):
    """Unified search for Constitutional Court decisions: both norm control and individual applications"""
    return await call_mcp_tool("search_anayasa_unified", request.dict())

@router.get("/anayasa/document", summary="Get Constitutional Court Document")
async def get_anayasa_document(
    document_url: str = Query(..., description="Document URL from search results"),
    page_number: int = Query(default=1, ge=1, description="Page number for paginated content")
):
    """Get Constitutional Court decision document"""
    return await call_mcp_tool("get_anayasa_document_unified", {
        "document_url": document_url,
        "page_number": page_number
    })

# UYUŞMAZLIK MAHKEMESİ (JURISDICTIONAL DISPUTES COURT)
@router.post("/uyusmazlik/search", summary="Search Jurisdictional Disputes Court Decisions")
async def search_uyusmazlik_decisions(request: SearchUyusmazlikRequest):
    """Search Uyuşmazlık Mahkemesi decisions for jurisdictional disputes"""
    return await call_mcp_tool("search_uyusmazlik_decisions", request.dict())

@router.get("/uyusmazlik/document", summary="Get Jurisdictional Disputes Document")
async def get_uyusmazlik_document(document_url: str = Query(..., description="Document URL")):
    """Get Uyuşmazlık Mahkemesi decision text from URL in Markdown format"""
    return await call_mcp_tool("get_uyusmazlik_document_markdown_from_url", {"document_url": document_url})

# KİK (PUBLIC PROCUREMENT AUTHORITY)
@router.post("/kik/search", summary="Search Public Procurement Authority Decisions")
async def search_kik_decisions(request: SearchKikRequest):
    """Search Public Procurement Authority (KİK) decisions for procurement law disputes"""
    return await call_mcp_tool("search_kik_decisions", request.dict())

@router.get("/kik/document/{decision_id}", summary="Get KİK Document")
async def get_kik_document(
    decision_id: str, 
    page_number: int = Query(default=1, ge=1, description="Page number")
):
    """Get Public Procurement Authority (KİK) decision text in paginated Markdown format"""
    return await call_mcp_tool("get_kik_document_markdown", {
        "karar_id": decision_id,
        "page_number": page_number
    })

# REKABET KURUMU (COMPETITION AUTHORITY)
@router.post("/rekabet/search", summary="Search Competition Authority Decisions")
async def search_rekabet_decisions(request: SearchRekabetRequest):
    """Search Competition Authority (Rekabet Kurumu) decisions for competition law and antitrust"""
    return await call_mcp_tool("search_rekabet_kurumu_decisions", request.dict())

@router.get("/rekabet/document/{decision_id}", summary="Get Competition Authority Document")
async def get_rekabet_document(
    decision_id: str,
    page_number: int = Query(default=1, ge=1, description="Page number")
):
    """Get Competition Authority decision text in paginated Markdown format"""
    return await call_mcp_tool("get_rekabet_kurumu_document", {
        "karar_id": decision_id,
        "page_number": page_number
    })

# SAYIŞTAY (COURT OF ACCOUNTS)
@router.post("/sayistay/search", summary="Search Court of Accounts Decisions")
async def search_sayistay_decisions(request: SearchSayistayRequest):
    """Search Sayıştay decisions unified across all three decision types"""
    return await call_mcp_tool("search_sayistay_unified", request.dict())

@router.get("/sayistay/document/{decision_id}", summary="Get Court of Accounts Document")
async def get_sayistay_document(
    decision_id: str,
    decision_type: str = Query(..., description="Decision type: genel_kurul, temyiz_kurulu, or daire")
):
    """Get Sayıştay decision document in Markdown format"""
    return await call_mcp_tool("get_sayistay_document_unified", {
        "decision_id": decision_id,
        "decision_type": decision_type
    })

# KVKK (PERSONAL DATA PROTECTION AUTHORITY)
@router.post("/kvkk/search", summary="Search KVKK Data Protection Decisions")
async def search_kvkk_decisions(request: SearchKvkkRequest):
    """Search KVKK data protection authority decisions"""
    return await call_mcp_tool("search_kvkk_decisions", request.dict())

@router.get("/kvkk/document", summary="Get KVKK Document")
async def get_kvkk_document(
    decision_url: str = Query(..., description="KVKK decision URL"),
    page_number: int = Query(default=1, ge=1, description="Page number")
):
    """Get KVKK decision document in Markdown format"""
    return await call_mcp_tool("get_kvkk_document_markdown", {
        "decision_url": decision_url,
        "page_number": page_number
    })

# BDDK (BANKING REGULATION AND SUPERVISION AGENCY)
@router.post("/bddk/search", summary="Search BDDK Banking Regulation Decisions")
async def search_bddk_decisions(request: SearchBddkRequest):
    """Search BDDK banking regulation decisions"""
    return await call_mcp_tool("search_bddk_decisions", request.dict())

@router.get("/bddk/document/{document_id}", summary="Get BDDK Document")
async def get_bddk_document(
    document_id: str,
    page_number: int = Query(default=1, ge=1, description="Page number")
):
    """Get BDDK decision document as Markdown"""
    return await call_mcp_tool("get_bddk_document_markdown", {
        "document_id": document_id,
        "page_number": page_number
    })

# UTILITY ENDPOINTS
@router.get("/tools", summary="List Available Tools")
async def list_tools():
    """List all available Yargi-MCP tools and endpoints"""
    return {
        "total_tools": 38,
        "categories": {
            "health": ["check_government_servers_health"],
            "bedesten_unified": ["search_bedesten_unified", "get_bedesten_document_markdown"],
            "emsal": ["search_emsal_detailed_decisions", "get_emsal_document_markdown"],
            "anayasa": ["search_anayasa_unified", "get_anayasa_document_unified"],
            "uyusmazlik": ["search_uyusmazlik_decisions", "get_uyusmazlik_document_markdown_from_url"],
            "kik": ["search_kik_decisions", "get_kik_document_markdown"],
            "rekabet": ["search_rekabet_kurumu_decisions", "get_rekabet_kurumu_document"],
            "sayistay": ["search_sayistay_unified", "get_sayistay_document_unified"],
            "kvkk": ["search_kvkk_decisions", "get_kvkk_document_markdown"],
            "bddk": ["search_bddk_decisions", "get_bddk_document_markdown"]
        },
        "courts_covered": [
            "Yargıtay (Supreme Court of Appeals)",
            "Danıştay (Council of State)",
            "Anayasa Mahkemesi (Constitutional Court)",
            "Bölge Adliye Mahkemeleri (Regional Courts)",
            "Yerel Mahkemeler (Local Courts)",
            "Uyuşmazlık Mahkemesi (Jurisdictional Disputes Court)",
            "KİK (Public Procurement Authority)",
            "Rekabet Kurumu (Competition Authority)",
            "Sayıştay (Court of Accounts)",
            "KVKK (Personal Data Protection Authority)",
            "BDDK (Banking Regulation and Supervision Agency)"
        ]
    }

@router.get("/stats", summary="Get API Statistics")
async def get_api_stats():
    """Get API usage statistics and information"""
    return {
        "service": "Yargi-MCP REST API",
        "version": "1.0.0",
        "total_endpoints": 21,
        "search_endpoints": 10,
        "document_endpoints": 10,
        "utility_endpoints": 3,
        "supported_courts": 11,
        "features": [
            "Turkish legal database search",
            "Court decision retrieval",
            "Markdown document formatting",
            "Pagination support",
            "Advanced filtering",
            "Multi-court unified search"
        ],
        "last_updated": datetime.now().isoformat()
    }