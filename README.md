# Yargı AI API

OpenRouter LLM-powered Turkish Legal Search API with MCP integration.

## Features

- 🤖 **Multiple AI Models**: Claude 3.5 Sonnet, GPT-4o, Gemini Pro, Llama 3.1, Mistral
- ⚖️ **Turkish Legal Database**: 21 MCP tools for comprehensive legal search
- 🔧 **Flexible Model Selection**: Switch between models via API parameter
- 📊 **Token Usage Tracking**: Detailed cost monitoring
- 🔄 **Fallback System**: Works even when external services are down

## Quick Start

### Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd yargi-ai-api

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENROUTER_API_KEY=your_key_here
export OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Run server
python main.py
```

### Docker

```bash
# Build image
docker build -t yargi-ai-api .

# Run container
docker run -p 8001:8001 \
  -e OPENROUTER_API_KEY=your_key_here \
  -e OPENROUTER_MODEL=anthropic/claude-3.5-sonnet \
  yargi-ai-api
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
