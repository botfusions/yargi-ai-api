# Turkish Legal AI API - Complete

> Comprehensive REST API exposing 41+ Turkish legal database tools from yargi-mcp and mevzuat-mcp servers

## 🚀 Overview

This API provides REST endpoints for all Turkish legal databases and court systems, integrating **38 yargi-mcp tools** and **3 mevzuat-mcp tools** into a unified, developer-friendly interface.

### 📊 Quick Stats
- **41+ MCP Tools** exposed as REST endpoints
- **33 REST Endpoints** across 11 legal systems
- **9 Court Systems** and regulatory authorities
- **Complete Turkish legal framework** coverage

## 🏛️ Supported Court Systems

### Primary Courts
- **Yargıtay** (Supreme Court of Appeals) - 52 chambers/boards
- **Danıştay** (Council of State) - 27 chambers/boards
- **Anayasa Mahkemesi** (Constitutional Court) - Individual applications & norm control
- **Bölge Adliye Mahkemeleri** (Regional Courts of Appeal)
- **Yerel Mahkemeler** (Local Courts)

### Specialized Courts & Authorities
- **Uyuşmazlık Mahkemesi** (Jurisdictional Disputes Court)
- **KİK** (Public Procurement Authority)
- **Rekabet Kurumu** (Competition Authority)
- **Sayıştay** (Court of Accounts) - 8 chambers
- **KVKK** (Personal Data Protection Authority)
- **BDDK** (Banking Regulation and Supervision Agency)

### Legislation Database
- **Turkish Legislation Database** (mevzuat.gov.tr) - All laws and regulations

## 🛠️ Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install MCP Servers
```bash
# Install yargi-mcp (38 tools)
uvx yargi-mcp
# or
pip install yargi-mcp

# Install mevzuat-mcp (3 tools)  
uvx mevzuat-mcp
# or
pip install mevzuat-mcp
```

### 3. Run the API
```bash
python main.py
```

The API will be available at `http://localhost:8001`

### 4. Access Documentation
- **Interactive Docs**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **Health Check**: http://localhost:8001/health

## 📚 API Documentation

### System Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirect to documentation |
| `/health` | GET | API health status |
| `/api/info` | GET | Complete API information |
| `/api/test` | GET | Test endpoint functionality |
| `/api/overview` | GET | Full API overview |

## 🏛️ Yargi-MCP Endpoints (38 tools)

### Multi-Court Search (Bedesten Unified)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/health` | GET | Check government servers status |
| `/api/yargi/bedesten/search` | POST | Search multiple courts (Yargıtay, Danıştay, etc.) |
| `/api/yargi/bedesten/document/{id}` | GET | Get court decision document |

### Constitutional Court (Anayasa Mahkemesi)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/anayasa/search` | POST | Search Constitutional Court decisions |
| `/api/yargi/anayasa/document` | GET | Get Constitutional Court document |

### Emsal Precedent Decisions
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/emsal/search` | POST | Search precedent decisions |
| `/api/yargi/emsal/document/{id}` | GET | Get precedent decision document |

### Jurisdictional Disputes Court (Uyuşmazlık Mahkemesi)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/uyusmazlik/search` | POST | Search jurisdictional disputes |
| `/api/yargi/uyusmazlik/document` | GET | Get jurisdictional dispute document |

### Public Procurement Authority (KİK)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/kik/search` | POST | Search KİK procurement decisions |
| `/api/yargi/kik/document/{id}` | GET | Get KİK decision document |

### Competition Authority (Rekabet Kurumu)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/rekabet/search` | POST | Search competition law decisions |
| `/api/yargi/rekabet/document/{id}` | GET | Get competition authority document |

### Court of Accounts (Sayıştay)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/sayistay/search` | POST | Search court of accounts decisions |
| `/api/yargi/sayistay/document/{id}` | GET | Get court of accounts document |

### Personal Data Protection Authority (KVKK)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/kvkk/search` | POST | Search KVKK data protection decisions |
| `/api/yargi/kvkk/document` | GET | Get KVKK decision document |

### Banking Regulation Agency (BDDK)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/bddk/search` | POST | Search BDDK banking regulation decisions |
| `/api/yargi/bddk/document/{id}` | GET | Get BDDK decision document |

### Utility
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yargi/tools` | GET | List all available yargi tools |
| `/api/yargi/stats` | GET | Get yargi API statistics |

## 📖 Mevzuat-MCP Endpoints (3 tools)

### Legislation Search
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mevzuat/search` | POST | Advanced legislation search |
| `/api/mevzuat/search/by-name` | GET | Search by legislation name |
| `/api/mevzuat/search/by-number` | GET | Search by legislation number |
| `/api/mevzuat/search/full-text` | GET | Full-text content search |

### Legislation Structure & Content
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mevzuat/legislation/{id}/structure` | GET | Get legislation table of contents |
| `/api/mevzuat/legislation/{id}/article/{article_id}` | GET | Get specific article content |

### Information & Utilities
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/mevzuat/types` | GET | Available legislation types |
| `/api/mevzuat/popular` | GET | Important/popular legislation |
| `/api/mevzuat/tools` | GET | Available mevzuat tools |
| `/api/mevzuat/stats` | GET | Mevzuat API statistics |

## 🔍 Example Usage

### Search Multiple Courts
```bash
curl -X POST "http://localhost:8001/api/yargi/bedesten/search" \
  -H "Content-Type: application/json" \
  -d '{
    "phrase": "mülkiyet hakkı",
    "court_types": ["YARGITAYKARARI", "DANISTAYKARAR"],
    "pageNumber": 1
  }'
```

### Search Constitutional Court
```bash
curl -X POST "http://localhost:8001/api/yargi/anayasa/search" \
  -H "Content-Type: application/json" \
  -d '{
    "decision_type": "bireysel_basvuru",
    "keywords": ["ifade özgürlüğü"],
    "page_to_fetch": 1
  }'
```

### Search Turkish Legislation
```bash
curl -X POST "http://localhost:8001/api/mevzuat/search" \
  -H "Content-Type: application/json" \
  -d '{
    "mevzuat_adi": "Türk Ceza Kanunu",
    "page_number": 1,
    "page_size": 10
  }'
```

### Get Specific Law by Number
```bash
curl "http://localhost:8001/api/mevzuat/search/by-number?number=5237"
```

## 🏗️ Architecture

### MCP Integration
The API acts as a REST wrapper around MCP (Model Context Protocol) servers:

```
[REST API] → [MCP Tools] → [Turkish Legal Databases]
    ↓              ↓                    ↓
FastAPI     yargi-mcp (38 tools)   Government APIs
           mevzuat-mcp (3 tools)   mevzuat.gov.tr
```

### Key Features
- **Unified Interface**: Single API for all Turkish legal databases
- **Advanced Search**: Full-text, filtered, and paginated search
- **Document Retrieval**: Markdown-formatted legal documents
- **Real-time Data**: Direct integration with government databases
- **Comprehensive Coverage**: All court levels and regulatory authorities

## 🔧 Configuration

### Environment Variables
```bash
PORT=8001                    # API server port
HOST=0.0.0.0                # API server host
ENVIRONMENT=production       # Environment type
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["python", "main.py"]
```

## 📈 Performance & Limits

### Rate Limits
- Government servers have inherent rate limits
- Recommended: Max 10 concurrent requests
- Consider implementing client-side caching

### Response Times
- Simple searches: 1-3 seconds
- Complex searches: 3-10 seconds  
- Document retrieval: 1-5 seconds

### Data Freshness
- Court decisions: Real-time from government databases
- Legislation: Updated as published in Official Gazette

## 🔒 Security

### API Security
- CORS enabled for all origins (configure for production)
- Input validation via Pydantic models
- Error handling prevents information leakage

### Data Handling
- No sensitive data stored locally
- All queries forwarded to official government databases
- Legal documents returned as publicly available

## 📝 Legal & Compliance

### Data Sources
- All data sourced from official Turkish government databases
- Content accuracy maintained by relevant authorities
- API provides access, not storage of legal documents

### Usage Terms
- API for legal research and information purposes
- Professional legal advice still required for decisions
- Comply with Turkish government website terms of service

## 🚀 Deployment Options

### Local Development
```bash
python main.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8001
```

### Docker Container
```bash
docker build -t turkish-legal-api .
docker run -p 8001:8001 turkish-legal-api
```

### Cloud Deployment
- Compatible with Heroku, Railway, Fly.io
- Requires Python 3.11+ runtime
- Memory: Minimum 512MB recommended

## 🤝 Contributing

### Development Setup
1. Clone repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install MCP servers: `uvx yargi-mcp && uvx mevzuat-mcp`
4. Run tests: `python -m pytest`
5. Start development server: `python main.py`

### Adding New Features
- Follow FastAPI patterns established in existing endpoints
- Add comprehensive documentation and examples
- Ensure proper error handling and validation

## 📞 Support

### Documentation
- Interactive API docs: `/docs`
- OpenAPI specification: `/openapi.json`
- This README and inline code documentation

### Issues & Feedback
- Technical issues: Check server logs and MCP tool status
- Feature requests: Submit with clear use cases
- Data accuracy: Verify against original government sources

---

**Turkish Legal AI API v2.0.0** - Comprehensive access to Turkish legal databases through a unified REST interface.