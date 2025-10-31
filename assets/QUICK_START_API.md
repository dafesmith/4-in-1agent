# Quick Start: API Deployment (5 Minutes)

## TL;DR
Replace local models with OpenAI API - same functionality, no GPU needed.

---

## 1️⃣ Get OpenAI Key (2 min)
```bash
# Go to: https://platform.openai.com/api-keys
# Click: "Create new secret key"
# Copy key: sk-proj-xxxxxxxxxxxxx
```

---

## 2️⃣ Create `.env` File (1 min)
```bash
cd assets/backend
cp .env.example .env
nano .env
```

Add your key:
```bash
OPENAI_API_KEY=sk-proj-your-key-here
```
Save and exit (Ctrl+X, Y, Enter)

---

## 3️⃣ Update 4 Code Files (2 min)

### File 1: `backend/agent.py` (line 161-164)
```python
# Change:
self.model_client = AsyncOpenAI(
    base_url=f"http://{self.current_model}:8000/v1",
    api_key="api_key"
)

# To:
import os
self.model_client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### File 2: `backend/vector_store.py` (lines 32-58)
```python
# Delete CustomEmbeddings class, replace __init__ with:
from langchain_openai import OpenAIEmbeddings

def __init__(self, embeddings=None, uri: str = "http://milvus:19530", on_source_deleted=None):
    if embeddings is None:
        import os
        self.embeddings = OpenAIEmbeddings(
            model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
    else:
        self.embeddings = embeddings
    # ... rest stays the same
```

### File 3: `backend/tools/mcp_servers/code_generation.py` (lines 28, 42-45)
```python
# Line 28: Change model name
import os
model_name = os.getenv("CODE_GEN_MODEL", "gpt-4-turbo")

# Lines 42-45: Change client
model_client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### File 4: `backend/tools/mcp_servers/image_understanding.py` (lines 45-49)
```python
# Change:
import os
model_name = os.getenv("VISION_MODEL", "gpt-4-turbo")
model_client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

## 4️⃣ Deploy (2 min)
```bash
cd assets

# Stop old containers (if running)
docker compose down

# Start with API configuration
docker compose -f docker-compose-api.yml up -d --build

# Check status
docker compose -f docker-compose-api.yml ps

# View logs
docker logs -f backend
```

---

## 5️⃣ Test (1 min)
```bash
# Open browser
open http://localhost:3000

# Try these:
1. "Hello!" → Should respond
2. "Write a Python hello world" → Should generate code
3. Upload a PDF → Ask questions about it
```

---

## ✅ Success Checklist
- [ ] OpenAI API key obtained
- [ ] `.env` file created with API key
- [ ] 4 code files updated
- [ ] Containers running (`docker ps`)
- [ ] UI accessible at http://localhost:3000
- [ ] Chat responding correctly

---

## ❌ Troubleshooting

**"Invalid API key"**
```bash
cat backend/.env | grep OPENAI_API_KEY
# Verify key starts with sk-
docker restart backend
```

**"Connection refused"**
```bash
# Wait 30 seconds for services to start
docker logs backend
docker logs milvus-standalone
```

**"Rate limit exceeded"**
- Wait a few minutes
- Check usage: https://platform.openai.com/usage

---

## 💰 Cost
- Light use: ~$15/month
- Medium use: ~$70/month
- Heavy use: ~$300/month

Set spending limit: https://platform.openai.com/account/limits

---

## 📖 Full Guide
See `API_DEPLOYMENT_GUIDE.md` for detailed instructions.

---

## 🎯 What Changed?

| Before (Local) | After (API) |
|---------------|-------------|
| gpt-oss-120b container | OpenAI GPT-4 API |
| qwen3-embedding container | OpenAI Embeddings API |
| deepseek-coder container | OpenAI GPT-4 API |
| qwen2.5-vl container | OpenAI Vision API |
| 120GB GPU needed | No GPU needed |
| ~100GB models | ~500MB |
| 20min startup | 2min startup |
| $0/month | $15-300/month |

**Kept (still local):**
- PostgreSQL (chat history)
- Milvus (vector database)
- Backend (FastAPI)
- Frontend (Next.js)

---

**That's it! You're done.**
