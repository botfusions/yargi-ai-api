# Yargı AI API

Basit, hızlı ve kolay Turkish Legal API - Windows'ta çalışır!

## ✨ Özellikler

- ⚡ **Hızlı Kurulum**: 3 dakikada çalışır
- 🪟 **Windows Uyumlu**: PowerShell ile kolay kurulum
- 🔧 **Basit API**: FastAPI ile hazır endpoint'ler
- 📚 **Interaktif Dokümantasyon**: Otomatik API docs
- 🚀 **Genişletilebilir**: Kendi endpoint'lerinizi ekleyin

## 🚀 Windows'ta Hızlı Başlangıç

### 1️⃣ Python Kurulumu (Eğer yoksa)

- [Python 3.8+](https://www.python.org/downloads/) indirin ve kurun
- Kurulum sırasında **"Add Python to PATH"** seçeneğini işaretleyin

### 2️⃣ Projeyi İndirin

**Yöntem A: Git ile**
```powershell
git clone https://github.com/botfusions/yargi-ai-api.git
cd yargi-ai-api
```

**Yöntem B: ZIP ile**
1. GitHub'dan ZIP olarak indirin
2. `yargi-ai-api` klasörüne çıkarın
3. PowerShell'de klasöre gidin:
```powershell
cd C:\Users\user\Downloads\yargi-ai-api
```

### 3️⃣ Bağımlılıkları Kurun

```powershell
pip install -r requirements.txt
```

### 4️⃣ API'yi Başlatın

```powershell
python main.py
```

### 5️⃣ Tarayıcınızda Açın

- **Ana Sayfa**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

## 🐧 Linux/Mac Kurulum

```bash
# Clone repository
git clone https://github.com/botfusions/yargi-ai-api.git
cd yargi-ai-api

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

## 🐳 Docker

```bash
# Build image
docker build -t yargi-ai-api .

# Run container
docker run -p 8001:8001 yargi-ai-api
```

## API Endpoints

### Health Check
```
GET /health
```

### Legal Search
```
POST /api/search?query=iş hukuku&model=anthropic/claude-3.5-sonnet&detailed=true
```

### Available Models
```
GET /api/models
```

### Model Comparison
```
POST /api/compare-models?query=sözleşme feshi
```

## Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `OPENROUTER_MODEL`: Default model (default: anthropic/claude-3.5-sonnet)
- `PORT`: Server port (default: 8001)
- `HOST`: Server host (default: 0.0.0.0)

## Recommended Models

| Model | Cost | Use Case |
|-------|------|----------|
| anthropic/claude-3.5-sonnet | $3.00/1M | Premium legal analysis |
| google/gemini-pro-1.5 | $1.25/1M | Balanced performance |
| meta-llama/llama-3.1-70b | $0.40/1M | Budget-friendly |

## License

MIT License
