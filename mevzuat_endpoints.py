"""
Mevzuat-MCP REST API Endpoints
Exposes Turkish legislation database tools as REST endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
import subprocess
import json
import tempfile
import os

router = APIRouter(prefix="/api/mevzuat", tags=["Mevzuat MCP Tools"])

# Pydantic models for request/response validation
class SearchMevzuatRequest(BaseModel):
    mevzuat_adi: Optional[str] = Field(default=None, description="Name of legislation or keyword")
    mevzuat_no: Optional[str] = Field(default=None, description="Specific legislation number (e.g., '5237')")
    mevzuat_turleri: Optional[Union[List[str], str]] = Field(
        default=None, 
        description="Filter by legislation types: KANUN, CB_KARARNAME, YONETMELIK, CB_YONETMELIK, CB_KARAR, CB_GENELGE, KHK, TUZUK, KKY, UY, TEBLIGLER, MULGA"
    )
    phrase: Optional[str] = Field(default=None, description="Search term in FULL TEXT of legislation")
    resmi_gazete_sayisi: Optional[str] = Field(default=None, description="Official Gazette issue number")
    page_number: int = Field(default=1, ge=1, description="Page number for pagination")
    page_size: int = Field(default=10, ge=1, le=50, description="Results per page")
    sort_field: str = Field(
        default="RESMI_GAZETE_TARIHI", 
        description="Sort field: RESMI_GAZETE_TARIHI, KAYIT_TARIHI, MEVZUAT_NUMARASI"
    )
    sort_direction: str = Field(default="desc", description="Sort direction: desc (newest first) or asc (oldest first)")

class MevzuatSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_count: int
    page_number: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

class ArticleTreeResponse(BaseModel):
    mevzuat_id: str
    title: str
    structure: List[Dict[str, Any]]

class ArticleContentResponse(BaseModel):
    mevzuat_id: str
    madde_id: str
    title: str
    content: str
    markdown_content: str

# Helper function to call MCP tools
async def call_mcp_tool(tool_name: str, parameters: dict) -> dict:
    """Call Mevzuat MCP tool via command line interface"""
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
    'search_mevzuat': 'from mcp__mevzuat_mcp__search_mevzuat import mcp__mevzuat_mcp__search_mevzuat as tool_func',
    'get_mevzuat_article_tree': 'from mcp__mevzuat_mcp__get_mevzuat_article_tree import mcp__mevzuat_mcp__get_mevzuat_article_tree as tool_func',
    'get_mevzuat_article_content': 'from mcp__mevzuat_mcp__get_mevzuat_article_content import mcp__mevzuat_mcp__get_mevzuat_article_content as tool_func'
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

# LEGISLATION SEARCH ENDPOINTS
@router.post("/search", response_model=MevzuatSearchResponse, summary="Search Turkish Legislation")
async def search_mevzuat(request: SearchMevzuatRequest):
    """
    Search Turkish legislation on mevzuat.gov.tr
    
    **Search Types:**
    - **Title Search**: Use `mevzuat_adi` for legislation title/name search
    - **Full-Text Search**: Use `phrase` for content search within legislation text
    - **Number Search**: Use `mevzuat_no` for specific legislation number (e.g., "5237")
    
    **Legislation Types:**
    - **KANUN**: Law (Kanun)
    - **CB_KARARNAME**: Presidential Decree (Cumhurbaşkanlığı Kararnamesi)
    - **YONETMELIK**: Regulation (Yönetmelik)
    - **CB_YONETMELIK**: Presidential Regulation (Cumhurbaşkanlığı Yönetmeliği)
    - **CB_KARAR**: Presidential Decision (Cumhurbaşkanlığı Kararı)
    - **CB_GENELGE**: Presidential Circular (Cumhurbaşkanlığı Genelgesi)
    - **KHK**: Decree Law (Kanun Hükmünde Kararname)
    - **TUZUK**: Statute/Bylaw (Tüzük)
    - **KKY**: Institutional Regulations (Kurum ve Kuruluş Yönetmelikleri)
    - **UY**: Procedures and Regulations (Usul ve Yönetmelikler)
    - **TEBLIGLER**: Communiqué (Tebliğler)
    - **MULGA**: Repealed (Mülga)
    """
    result = await call_mcp_tool("search_mevzuat", request.dict(exclude_none=True))
    
    # Transform response to match our model
    return MevzuatSearchResponse(
        results=result.get("results", []),
        total_count=result.get("total_count", 0),
        page_number=result.get("page_number", 1),
        page_size=result.get("page_size", 10),
        total_pages=result.get("total_pages", 0),
        has_next=result.get("has_next", False),
        has_previous=result.get("has_previous", False)
    )

@router.get("/search/by-name", summary="Search Legislation by Name")
async def search_by_name(
    name: str = Query(..., description="Legislation name or keyword"),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=50, description="Page size"),
    sort: str = Query(default="RESMI_GAZETE_TARIHI", description="Sort field"),
    order: str = Query(default="desc", description="Sort order: desc or asc")
):
    """Search legislation by name/title (quick search endpoint)"""
    return await search_mevzuat(SearchMevzuatRequest(
        mevzuat_adi=name,
        page_number=page,
        page_size=size,
        sort_field=sort,
        sort_direction=order
    ))

@router.get("/search/by-number", summary="Search Legislation by Number")
async def search_by_number(
    number: str = Query(..., description="Legislation number (e.g., '5237')"),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=50, description="Page size")
):
    """Search legislation by specific number (e.g., Turkish Penal Code 5237)"""
    return await search_mevzuat(SearchMevzuatRequest(
        mevzuat_no=number,
        page_number=page,
        page_size=size
    ))

@router.get("/search/full-text", summary="Full-Text Search in Legislation")
async def search_full_text(
    query: str = Query(..., description="Search term in legislation content"),
    types: Optional[List[str]] = Query(default=None, description="Legislation types to filter"),
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=50, description="Page size")
):
    """Search within the full text content of legislation"""
    return await search_mevzuat(SearchMevzuatRequest(
        phrase=query,
        mevzuat_turleri=types,
        page_number=page,
        page_size=size
    ))

# LEGISLATION STRUCTURE AND CONTENT ENDPOINTS
@router.get("/legislation/{mevzuat_id}/structure", response_model=ArticleTreeResponse, summary="Get Legislation Structure")
async def get_legislation_structure(mevzuat_id: str):
    """
    Get the table of contents (article tree) for specific legislation
    
    This shows the hierarchical structure of the legislation including:
    - Chapters (Bölüm)
    - Sections (Kısım) 
    - Articles (Madde)
    - Paragraphs and sub-items
    
    **Parameters:**
    - `mevzuat_id`: The ID obtained from search results (e.g., '343829')
    """
    result = await call_mcp_tool("get_mevzuat_article_tree", {"mevzuat_id": mevzuat_id})
    
    return ArticleTreeResponse(
        mevzuat_id=mevzuat_id,
        title=result.get("title", ""),
        structure=result.get("structure", [])
    )

@router.get("/legislation/{mevzuat_id}/article/{madde_id}", response_model=ArticleContentResponse, summary="Get Article Content")
async def get_article_content(mevzuat_id: str, madde_id: str):
    """
    Get the full text content of a specific article
    
    Returns clean Markdown-formatted text of the article content.
    
    **Parameters:**
    - `mevzuat_id`: The legislation ID from search results
    - `madde_id`: The specific article ID from the structure endpoint (e.g., '2596801')
    """
    result = await call_mcp_tool("get_mevzuat_article_content", {
        "mevzuat_id": mevzuat_id,
        "madde_id": madde_id
    })
    
    return ArticleContentResponse(
        mevzuat_id=mevzuat_id,
        madde_id=madde_id,
        title=result.get("title", ""),
        content=result.get("content", ""),
        markdown_content=result.get("markdown_content", "")
    )

# UTILITY AND INFORMATION ENDPOINTS
@router.get("/types", summary="Get Available Legislation Types")
async def get_legislation_types():
    """Get list of all available legislation types with descriptions"""
    return {
        "legislation_types": {
            "KANUN": {
                "name": "Kanun",
                "description": "Law - Primary legislation enacted by Parliament",
                "english": "Law"
            },
            "CB_KARARNAME": {
                "name": "Cumhurbaşkanlığı Kararnamesi",
                "description": "Presidential Decree - Executive orders by the President",
                "english": "Presidential Decree"
            },
            "YONETMELIK": {
                "name": "Yönetmelik", 
                "description": "Regulation - Administrative regulations",
                "english": "Regulation"
            },
            "CB_YONETMELIK": {
                "name": "Cumhurbaşkanlığı Yönetmeliği",
                "description": "Presidential Regulation - Regulations issued by the President",
                "english": "Presidential Regulation"
            },
            "CB_KARAR": {
                "name": "Cumhurbaşkanlığı Kararı",
                "description": "Presidential Decision - Specific decisions by the President",
                "english": "Presidential Decision"
            },
            "CB_GENELGE": {
                "name": "Cumhurbaşkanlığı Genelgesi",
                "description": "Presidential Circular - Administrative circulars",
                "english": "Presidential Circular"
            },
            "KHK": {
                "name": "Kanun Hükmünde Kararname",
                "description": "Decree Law - Emergency decrees (historical)",
                "english": "Decree Law"
            },
            "TUZUK": {
                "name": "Tüzük",
                "description": "Statute/Bylaw - Organizational bylaws",
                "english": "Statute/Bylaw"
            },
            "KKY": {
                "name": "Kurum ve Kuruluş Yönetmelikleri",
                "description": "Institutional and Organizational Regulations",
                "english": "Institutional Regulations"
            },
            "UY": {
                "name": "Usul ve Yönetmelikler",
                "description": "Procedures and Regulations",
                "english": "Procedures and Regulations"
            },
            "TEBLIGLER": {
                "name": "Tebliğler",
                "description": "Communiqué - Official announcements",
                "english": "Communiqué"
            },
            "MULGA": {
                "name": "Mülga",
                "description": "Repealed - Cancelled/repealed legislation",
                "english": "Repealed"
            }
        },
        "total_types": 12,
        "usage_note": "These types can be used in the mevzuat_turleri parameter for filtering search results"
    }

@router.get("/popular", summary="Get Popular/Important Legislation")
async def get_popular_legislation():
    """Get a curated list of important and commonly referenced Turkish legislation"""
    return {
        "important_laws": {
            "civil_law": {
                "number": "4721",
                "name": "Türk Medeni Kanunu",
                "english": "Turkish Civil Code",
                "year": "2001",
                "description": "Fundamental civil law governing personal rights, family, property"
            },
            "penal_code": {
                "number": "5237", 
                "name": "Türk Ceza Kanunu",
                "english": "Turkish Penal Code",
                "year": "2004",
                "description": "Criminal law defining crimes and punishments"
            },
            "constitution": {
                "number": "2709",
                "name": "Türkiye Cumhuriyeti Anayasası", 
                "english": "Constitution of the Republic of Turkey",
                "year": "1982",
                "description": "Supreme law of Turkey"
            },
            "commercial_code": {
                "number": "6102",
                "name": "Türk Ticaret Kanunu",
                "english": "Turkish Commercial Code",
                "year": "2011",
                "description": "Commercial and corporate law"
            },
            "labor_law": {
                "number": "4857",
                "name": "İş Kanunu",
                "english": "Labor Law",
                "year": "2003", 
                "description": "Employment and labor relations"
            },
            "tax_procedure": {
                "number": "213",
                "name": "Vergi Usul Kanunu",
                "english": "Tax Procedure Law",
                "year": "1961",
                "description": "Tax administration and procedures"
            },
            "civil_procedure": {
                "number": "6100",
                "name": "Hukuk Muhakemeleri Kanunu",
                "english": "Code of Civil Procedure", 
                "year": "2011",
                "description": "Civil court procedures and litigation"
            },
            "criminal_procedure": {
                "number": "5271",
                "name": "Ceza Muhakemesi Kanunu",
                "english": "Code of Criminal Procedure",
                "year": "2004",
                "description": "Criminal court procedures and investigation"
            }
        },
        "search_tip": "Use the 'number' field with the /search/by-number endpoint to find these laws"
    }

@router.get("/tools", summary="List Available Mevzuat Tools")
async def list_mevzuat_tools():
    """List all available Mevzuat-MCP tools and endpoints"""
    return {
        "total_tools": 3,
        "mcp_tools": {
            "search_mevzuat": {
                "description": "Search Turkish legislation database",
                "parameters": ["mevzuat_adi", "mevzuat_no", "mevzuat_turleri", "phrase", "resmi_gazete_sayisi"],
                "endpoint": "/api/mevzuat/search"
            },
            "get_mevzuat_article_tree": {
                "description": "Get legislation structure/table of contents",
                "parameters": ["mevzuat_id"],
                "endpoint": "/api/mevzuat/legislation/{mevzuat_id}/structure"
            },
            "get_mevzuat_article_content": {
                "description": "Get specific article content in Markdown",
                "parameters": ["mevzuat_id", "madde_id"], 
                "endpoint": "/api/mevzuat/legislation/{mevzuat_id}/article/{madde_id}"
            }
        },
        "rest_endpoints": {
            "search_endpoints": 4,
            "structure_endpoints": 1,
            "content_endpoints": 1,
            "utility_endpoints": 3
        },
        "database": {
            "source": "mevzuat.gov.tr",
            "authority": "T.C. Adalet Bakanlığı",
            "english": "Ministry of Justice of the Republic of Turkey",
            "coverage": "All Turkish legislation and regulations"
        }
    }

@router.get("/stats", summary="Get Mevzuat API Statistics")
async def get_mevzuat_stats():
    """Get Mevzuat API usage statistics and information"""
    return {
        "service": "Mevzuat-MCP REST API",
        "version": "1.0.0",
        "total_endpoints": 9,
        "search_endpoints": 4,
        "content_endpoints": 2,
        "utility_endpoints": 3,
        "mcp_tools_exposed": 3,
        "database_info": {
            "source": "mevzuat.gov.tr",
            "type": "Turkish Legislation Database",
            "authority": "T.C. Adalet Bakanlığı (Ministry of Justice)",
            "coverage": "Complete Turkish legal framework"
        },
        "features": [
            "Legislation search by name/title",
            "Legislation search by number",
            "Full-text content search",
            "Hierarchical structure retrieval",
            "Article-level content access",
            "Markdown formatted output",
            "Advanced filtering by type",
            "Pagination support"
        ],
        "supported_types": 12,
        "last_updated": datetime.now().isoformat()
    }