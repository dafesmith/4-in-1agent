# API Deployment Guide

This guide explains how to deploy the multi-agent chatbot using **OpenAI APIs** instead of local models.

## 📋 Overview

**Architecture Change:**
- ❌ **Remove:** All local model containers (120GB+ VRAM required)
- ✅ **Keep:** Backend, Frontend, PostgreSQL, Milvus (vector DB)
- ✅ **Add:** OpenAI API integration (single API key)

**Benefits:**
- No GPU required
- No large model downloads (~100GB saved)
- Faster startup time (no model loading)
- Pay-as-you-go pricing
- Access to latest GPT-4 models

---

## 🔑 Step 1: Get OpenAI API Key

1. **Sign up for OpenAI:**
   - Go to: https://platform.openai.com/signup
   - Create account or sign in

2. **Add payment method:**
   - Go to: https://platform.openai.com/account/billing
   - Add credit card (required for API access)
   - Add initial credits ($5-20 recommended)

3. **Generate API key:**
   - Go to: https://platform.openai.com/api-keys
   - Click "Create new secret key"
   - Name it: "chatbot-app"
   - **IMPORTANT:** Copy the key (starts with `sk-proj-...`)
   - Save it securely (you won't see it again)

---

## 🛠️ Step 2: Configure Environment

1. **Navigate to backend directory:**
   ```bash
   cd /Users/dafesmith/Documents/multi-agent-chatbot/assets/backend
   ```

2. **Create `.env` file from example:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` file:**
   ```bash
   nano .env
   # or
   vim .env
   # or
   code .env
   ```

4. **Add your OpenAI API key:**
   ```bash
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   ```

5. **Save and close** the file

---

## 📦 Step 3: Update Code Files

### Required Code Changes

We need to modify 4 files to use OpenAI APIs instead of local endpoints:

#### 1. Agent (Supervisor LLM)
**File:** `backend/agent.py`

**Change lines 161-164:**

**Before:**
```python
self.model_client = AsyncOpenAI(
    base_url=f"http://{self.current_model}:8000/v1",
    api_key="api_key"
)
```

**After:**
```python
import os
self.model_client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

#### 2. Vector Store (Embeddings)
**File:** `backend/vector_store.py`

**Replace lines 32-58 (CustomEmbeddings class):**

**After:**
```python
from langchain_openai import OpenAIEmbeddings

class VectorStore:
    def __init__(
        self,
        embeddings=None,
        uri: str = "http://milvus:19530",
        on_source_deleted: Optional[Callable[[str], None]] = None
    ):
        try:
            # Use OpenAI embeddings instead of custom
            if embeddings is None:
                import os
                self.embeddings = OpenAIEmbeddings(
                    model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"),
                    openai_api_key=os.getenv("OPENAI_API_KEY")
                )
            else:
                self.embeddings = embeddings

            self.uri = uri
            self.on_source_deleted = on_source_deleted
            self._initialize_store()

            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

            logger.debug({"message": "VectorStore initialized with OpenAI embeddings"})
        except Exception as e:
            logger.error({"message": "Error initializing VectorStore", "error": str(e)}, exc_info=True)
            raise
```

**Note:** Remove the entire `CustomEmbeddings` class (lines 32-58)

---

#### 3. Code Generation Tool
**File:** `backend/tools/mcp_servers/code_generation.py`

**Change lines 28, 42-45:**

**Before:**
```python
model_name = "deepseek-coder:6.7b"

# ... (in write_code function)
model_client = AsyncOpenAI(
    base_url="http://deepseek-coder:8000/v1",
    api_key="ollama"
)
```

**After:**
```python
import os
model_name = os.getenv("CODE_GEN_MODEL", "gpt-4-turbo")

# ... (in write_code function)
model_client = AsyncOpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

#### 4. Image Understanding Tool
**File:** `backend/tools/mcp_servers/image_understanding.py`

**Change lines 45-49:**

**Before:**
```python
model_name = "Qwen2.5-VL-7B-Instruct"
model_client = OpenAI(
    base_url=f"http://qwen2.5-vl:8000/v1",
    api_key="api_key"
)
```

**After:**
```python
import os
model_name = os.getenv("VISION_MODEL", "gpt-4-turbo")
model_client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

---

## 🚀 Step 4: Deploy with Docker

1. **Stop any running containers:**
   ```bash
   cd /Users/dafesmith/Documents/multi-agent-chatbot/assets
   docker compose -f docker-compose.yml -f docker-compose-models.yml down
   ```

2. **Start with API configuration:**
   ```bash
   # Use the new API-only compose file
   docker compose -f docker-compose-api.yml up -d --build
   ```

3. **Check container status:**
   ```bash
   docker compose -f docker-compose-api.yml ps
   ```

4. **View logs:**
   ```bash
   # Backend logs
   docker logs -f backend

   # Frontend logs
   docker logs -f frontend
   ```

5. **Wait for services to be ready:**
   - Backend: ~30 seconds
   - Milvus: ~60 seconds
   - Frontend: ~20 seconds

6. **Access the application:**
   ```bash
   # Open in browser
   open http://localhost:3000
   ```

---

## ✅ Step 5: Verify Setup

### Test 1: Basic Chat
1. Go to http://localhost:3000
2. Type: "Hello, how are you?"
3. Should receive response from GPT-4

### Test 2: Code Generation
1. Type: "Write a Python function to calculate factorial"
2. Should generate working code

### Test 3: Image Understanding
1. Type: "Describe this image: https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
2. Should describe the image content

### Test 4: Document Q&A (RAG)
1. Upload a PDF document via sidebar
2. Select the document in "Select Sources"
3. Ask: "What is this document about?"
4. Should retrieve relevant content

---

## 🔍 Troubleshooting

### Error: "Invalid API key"
**Solution:**
```bash
# Check .env file
cat backend/.env | grep OPENAI_API_KEY

# Verify key format (should start with sk-proj- or sk-)
# Restart backend
docker restart backend
```

### Error: "Rate limit exceeded"
**Solution:**
- You've hit OpenAI's rate limit
- Wait a few minutes or upgrade your OpenAI tier
- Check usage: https://platform.openai.com/usage

### Error: "Insufficient quota"
**Solution:**
- Add more credits to your OpenAI account
- Go to: https://platform.openai.com/account/billing

### Error: "Milvus not ready"
**Solution:**
```bash
# Check Milvus status
docker logs milvus-standalone

# Restart Milvus
docker restart milvus-standalone

# Wait 60 seconds for initialization
```

### Error: "PostgreSQL connection refused"
**Solution:**
```bash
# Check PostgreSQL status
docker logs postgres

# Restart PostgreSQL
docker restart postgres
```

---

## 💰 Cost Estimation

### OpenAI Pricing (as of 2025)

| Model | Input (per 1K tokens) | Output (per 1K tokens) |
|-------|----------------------|------------------------|
| GPT-4 Turbo | $0.01 | $0.03 |
| GPT-3.5 Turbo | $0.0005 | $0.0015 |
| Text Embedding 3 Large | $0.00013 | N/A |
| GPT-4 Vision | $0.01 | $0.03 |

### Example Monthly Costs

**Light Usage (100 messages/day):**
- Chat: ~$10-20
- Embeddings: ~$1-2
- Vision: ~$2-5
- **Total: ~$13-27/month**

**Medium Usage (500 messages/day):**
- Chat: ~$50-100
- Embeddings: ~$5-10
- Vision: ~$10-20
- **Total: ~$65-130/month**

**Heavy Usage (2000 messages/day):**
- Chat: ~$200-400
- Embeddings: ~$20-40
- Vision: ~$40-80
- **Total: ~$260-520/month**

### Cost Optimization Tips

1. **Use GPT-3.5-turbo for simple queries:**
   ```bash
   # In .env
   SUPERVISOR_MODEL=gpt-3.5-turbo
   CODE_GEN_MODEL=gpt-3.5-turbo
   ```
   Savings: ~95% cheaper than GPT-4

2. **Use smaller embedding model:**
   ```bash
   EMBEDDING_MODEL=text-embedding-3-small
   ```
   Savings: ~60% cheaper

3. **Set token limits:**
   - Edit `agent.py` line 315-322
   - Add `max_tokens=1000` parameter

4. **Monitor usage:**
   - Dashboard: https://platform.openai.com/usage
   - Set up alerts for spending limits

---

## 🔄 Switching Between Models

### Use GPT-3.5 (Cheaper)
```bash
# Edit backend/.env
SUPERVISOR_MODEL=gpt-3.5-turbo
CODE_GEN_MODEL=gpt-3.5-turbo

# Restart backend
docker restart backend
```

### Use GPT-4 (Better Quality)
```bash
# Edit backend/.env
SUPERVISOR_MODEL=gpt-4-turbo
CODE_GEN_MODEL=gpt-4-turbo

# Restart backend
docker restart backend
```

### Mix Models (Optimized)
```bash
# Simple chat: GPT-3.5
SUPERVISOR_MODEL=gpt-3.5-turbo

# Complex code: GPT-4
CODE_GEN_MODEL=gpt-4-turbo

# Vision: GPT-4 (required)
VISION_MODEL=gpt-4-turbo
```

---

## 📊 Comparison: Local vs API

| Feature | Local Deployment | API Deployment |
|---------|-----------------|----------------|
| **Hardware** | 128GB GPU required | No GPU needed |
| **Setup Time** | 2-3 hours (model download) | 5-10 minutes |
| **Disk Space** | ~100GB | ~500MB |
| **Startup Time** | 10-20 minutes | 1-2 minutes |
| **Monthly Cost** | $0 (electricity only) | $50-500 (usage-based) |
| **Model Quality** | GPT-OSS-120B (good) | GPT-4 (excellent) |
| **Latency** | Low (local) | Medium (API calls) |
| **Scalability** | Limited by hardware | Unlimited |
| **Maintenance** | Manual updates | Automatic updates |

---

## 🔐 Security Best Practices

1. **Never commit .env file:**
   ```bash
   # Already in .gitignore
   echo "*.env" >> .gitignore
   ```

2. **Rotate API keys regularly:**
   - Rotate every 90 days
   - Use different keys for dev/prod

3. **Set usage limits:**
   - OpenAI dashboard → Usage limits
   - Set hard cap (e.g., $100/month)

4. **Monitor for anomalies:**
   - Check usage daily
   - Set up email alerts

5. **Use environment variables:**
   - Never hardcode API keys in code
   - Use Docker secrets in production

---

## 🎯 Next Steps

1. **Monitor costs:** https://platform.openai.com/usage
2. **Adjust models** based on usage patterns
3. **Set up alerts** for spending limits
4. **Deploy to production** (see PRODUCTION_DEPLOYMENT.md)
5. **Scale horizontally** (add more backend instances)

---

## 📚 Additional Resources

- OpenAI API Docs: https://platform.openai.com/docs
- OpenAI Pricing: https://openai.com/pricing
- Rate Limits: https://platform.openai.com/docs/guides/rate-limits
- Best Practices: https://platform.openai.com/docs/guides/production-best-practices

---

## 🆘 Support

For issues or questions:
1. Check logs: `docker logs backend`
2. Review OpenAI status: https://status.openai.com
3. Check API usage: https://platform.openai.com/usage
4. Verify .env configuration

---

**Last Updated:** 2025-10-30
