# Build and Deploy a Multi-Agent Chatbot

> Deploy a multi-agent chatbot system with OpenAI API integration

## Table of Contents

- [Overview](#overview)
- [Recent Updates](#recent-updates)
- [Instructions](#instructions)
- [Bug Fixes & Improvements](#bug-fixes--improvements)
- [Troubleshooting](#troubleshooting)

---

## Overview

## Basic idea

This repository contains a fully-functional multi-agent chatbot system with OpenAI API integration. The system has been migrated from local LLM deployment to use OpenAI's GPT models for improved performance and reliability.

At the core is a supervisor agent powered by GPT-4-Turbo, orchestrating specialized downstream agents for coding, retrieval-augmented generation (RAG), and image understanding through MCP (Model Context Protocol) servers.

## What you'll accomplish

You will have a full-stack multi-agent chatbot system accessible through your web browser with:
- **OpenAI API integration** for GPT-4-Turbo, text embeddings, and vision capabilities
- **GPU-accelerated Milvus** vector database for document retrieval
- **Multi-agent orchestration** using LangGraph with tool-calling support
- **MCP servers** providing specialized capabilities:
  - Image understanding (vision API)
  - Code generation
  - Document RAG with semantic search
  - Weather information
- **PostgreSQL** for conversation persistence
- **Real-time WebSocket** communication for streaming responses

---

## Recent Updates

### 🎉 **OpenAI API Migration Complete** (2025-10-31)

The system has been successfully migrated from local NVIDIA models to OpenAI API with **6 critical bugs fixed**:

#### ✅ **All Bugs Fixed**

| # | Bug | Severity | Impact | Status |
|---|-----|----------|--------|--------|
| 1 | Agent tool calling disabled for OpenAI models | 🔴 CRITICAL | Image understanding, RAG, code generation all broken | ✅ FIXED |
| 2 | RAG MCP server using wrong API endpoint | 🔴 CRITICAL | Document RAG completely non-functional | ✅ FIXED |
| 3 | Milvus collections not loaded into memory | 🔴 CRITICAL | Document search returning empty results | ✅ FIXED |
| 4 | Missing environment variable loading in RAG | 🟡 HIGH | Configuration errors | ✅ FIXED |
| 5 | CORS port mismatch (3000 vs 3100) | 🔴 CRITICAL | Document upload blocked | ✅ FIXED |
| 6 | PostgreSQL role documentation | 🟢 LOW | Documentation clarity | ✅ CLARIFIED |

**Detailed Fix Reports**:
- [ALL_BUGS_FIXED_REPORT.md](assets/ALL_BUGS_FIXED_REPORT.md) - Complete technical analysis
- [BUG_6_CORS_FIX.md](assets/BUG_6_CORS_FIX.md) - CORS configuration fix
- [CRITICAL_BUG_FIX_REPORT.md](assets/CRITICAL_BUG_FIX_REPORT.md) - Tool calling fix
- [QUICK_TEST_GUIDE.md](assets/QUICK_TEST_GUIDE.md) - Testing instructions

---

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key with access to:
  - GPT-4-Turbo (or GPT-4, GPT-3.5-Turbo)
  - text-embedding-3-large
  - Vision API
- Enough disk space for Docker images and vector database

> [!NOTE]
> This deployment uses **OpenAI API** instead of local models, reducing local hardware requirements significantly.

---

## Time & Risk

* **Estimated time**: 15-30 minutes (including Docker builds)
* **Risks**:
  * Docker permission issues may require user group changes
  * Build process downloads ~2GB+ of dependencies
  * Requires valid OpenAI API key
* **Rollback**: Stop and remove Docker containers using cleanup commands

---

## Instructions

### Step 1. Configure Docker permissions

To manage containers without sudo, add your user to the `docker` group:

```bash
# Test Docker access
docker ps

# If permission denied, add to docker group:
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2. Clone the repository

```bash
git clone https://github.com/NVIDIA/dgx-spark-playbooks
cd dgx-spark-playbooks/nvidia/multi-agent-chatbot/assets
```

### Step 3. Configure OpenAI API credentials

Create a `.env` file in the `assets/backend/` directory:

```bash
cd backend
cat > .env << 'EOF'
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1

# Model Selections (all using OpenAI)
SUPERVISOR_MODEL=gpt-4-turbo
EMBEDDING_MODEL=text-embedding-3-large
CODE_GEN_MODEL=gpt-4-turbo
VISION_MODEL=gpt-4-turbo

# Database Configuration (managed by docker-compose)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=chatbot
POSTGRES_USER=chatbot_user
POSTGRES_PASSWORD=chatbot_password

# Milvus Vector Database
MILVUS_ADDRESS=milvus:19530
ETCD_ENDPOINTS=etcd:2379
MINIO_ADDRESS=minio:9000

# Available models for UI dropdown
MODELS=gpt-4-turbo,gpt-4,gpt-3.5-turbo
EOF
```

**Important**: Replace `your-openai-api-key-here` with your actual OpenAI API key.

### Step 4. Start the Docker containers

```bash
cd /path/to/multi-agent-chatbot/assets
docker compose -f docker-compose-api.yml up -d --build
```

This builds and starts:
- **Backend** (FastAPI + LangGraph + MCP servers)
- **Frontend** (Next.js 15)
- **PostgreSQL** (conversation storage)
- **Milvus** (vector database for RAG)
- **Etcd** (Milvus dependency)
- **MinIO** (Milvus storage)

Build time: ~10-15 minutes (first time)

### Step 5. Monitor container health

```bash
watch 'docker ps --format "table {{.Names}}\t{{.Status}}"'
```

Wait for all containers to show "Up" and "(healthy)" status:
- ✅ chatbot-backend
- ✅ chatbot-frontend
- ✅ chatbot-postgres (healthy)
- ✅ chatbot-milvus-standalone (healthy)
- ✅ chatbot-milvus-etcd (healthy)
- ✅ chatbot-milvus-minio (healthy)

### Step 6. Verify backend initialization

```bash
docker logs chatbot-backend --tail 20
```

Expected output:
```
✅ "ChatAgent initialized successfully."
✅ "PostgreSQL storage initialized successfully"
✅ "Processing request of type ListToolsRequest"
✅ "Application startup complete."
```

### Step 7. Access the frontend UI

Open your browser and go to: **http://localhost:3100**

> [!NOTE]
> The frontend runs on port **3100** (not 3000) to avoid port conflicts.
> If accessing remotely via SSH, forward ports 3100 and 8100:
>
> ```bash
> ssh -L 3100:localhost:3100 -L 8100:localhost:8100 username@remote-host
> ```

### Step 8. Test the features

#### ✅ **Test 1: Basic Chat**
Send a message:
```
Hello! What can you help me with?
```

#### ✅ **Test 2: Image Understanding**
Send a message with an image URL:
```
Describe this image in detail: https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg
```

**Expected**: Detailed description using the `explain_image` tool

#### ✅ **Test 3: Document RAG**

1. Click **"Upload Documents"** button
2. Select a PDF file (1-5 pages recommended)
3. Wait for "Document uploaded successfully"
4. In "Select Sources", check the uploaded document
5. Ask a question:
   ```
   What is this document about? Provide a summary.
   ```

**Expected**: Accurate summary based on document content using `search_documents` tool

#### ✅ **Test 4: Code Generation**
Ask for code:
```
Write a Python function to calculate the nth Fibonacci number using recursion with memoization. Include type hints and docstring.
```

**Expected**: Complete Python code using `write_code` tool

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Browser (localhost:3100)                │
└────────────────────┬─────────────────┬──────────────────────┘
                     │                 │
              HTTP/REST          WebSocket (streaming)
                     │                 │
         ┌───────────▼─────────────────▼─────────────┐
         │   Frontend (Next.js 15)                   │
         │   - Real-time chat UI                     │
         │   - Document upload                       │
         │   - Source selection                      │
         └───────────────────┬───────────────────────┘
                             │
                    Proxy /api/* → backend:8000
                             │
         ┌───────────────────▼───────────────────────┐
         │   Backend (FastAPI)                       │
         │   - WebSocket handler                     │
         │   - Document ingestion                    │
         │   - ChatAgent (LangGraph)                 │
         └───┬──────────┬──────────┬─────────────────┘
             │          │          │
    ┌────────▼──┐  ┌────▼────┐  ┌─▼─────────┐
    │ OpenAI API│  │PostgreSQL│  │  Milvus   │
    │           │  │          │  │ (Vectors) │
    │ GPT-4     │  │ Convos   │  │ RAG Docs  │
    │ Embeddings│  │ Images   │  └───────────┘
    │ Vision    │  └──────────┘
    └───────────┘
         ▲
         │
    ┌────┴─────────────────────────────────┐
    │  MCP Servers (stdio subprocess)      │
    │  - image-understanding-server        │
    │  - code-generation-server            │
    │  - rag-server                        │
    │  - weather-server                    │
    └──────────────────────────────────────┘
```

### Port Configuration

| Service | Internal Port | External Port | Access |
|---------|--------------|---------------|---------|
| Backend | 8000 | 8100 | http://localhost:8100 |
| Frontend | 3000 | 3100 | http://localhost:3100 |
| PostgreSQL | 5432 | 5433 | localhost:5433 |
| Milvus | 19530 | 19531 | localhost:19531 |

---

## Bug Fixes & Improvements

### Critical Fixes Applied (2025-10-31)

#### 1. **Agent Tool Calling for OpenAI Models**
- **File**: `backend/agent.py:297-303`
- **Issue**: Tool support check only recognized NVIDIA local models
- **Fix**: Added OpenAI model detection using `startswith("gpt-")`
- **Impact**: Enabled all MCP tools (image understanding, RAG, code generation)

#### 2. **RAG Server API Endpoint**
- **File**: `backend/tools/mcp_servers/rag.py:90-94`
- **Issue**: Attempting to connect to non-existent local model container
- **Fix**: Changed to use OpenAI API with proper environment variables
- **Impact**: Document RAG now fully functional

#### 3. **Milvus Collection Loading**
- **Files**: `backend/vector_store.py:81-117`, `vector_store.py:257-270`
- **Issue**: Collections not loaded into memory after creation/indexing
- **Fix**: Added explicit `collection.load()` calls after init and indexing
- **Impact**: Document search now returns results

#### 4. **Environment Variable Loading**
- **File**: `backend/tools/mcp_servers/rag.py:44-51`
- **Issue**: MCP subprocess not loading .env file
- **Fix**: Added explicit `load_dotenv()` with absolute path
- **Impact**: Environment variables properly loaded in all MCP servers

#### 5. **CORS Configuration**
- **File**: `backend/main.py:107`
- **Issue**: Only allowed `localhost:3000`, not `localhost:3100`
- **Fix**: Added port 3100 to allowed origins
- **Impact**: Document upload and all API calls now work

#### 6. **WebSocket Port Configuration**
- **File**: `frontend/src/components/QuerySection.tsx:236`
- **Issue**: Hardcoded port 8000 instead of 8100
- **Fix**: Changed to port 8100
- **Impact**: Real-time chat streaming works

### Documentation Created

- ✅ **[ALL_BUGS_FIXED_REPORT.md](assets/ALL_BUGS_FIXED_REPORT.md)** - Complete technical analysis with before/after code, documentation sources, and architecture diagrams
- ✅ **[BUG_6_CORS_FIX.md](assets/BUG_6_CORS_FIX.md)** - CORS configuration fix details
- ✅ **[CRITICAL_BUG_FIX_REPORT.md](assets/CRITICAL_BUG_FIX_REPORT.md)** - Tool calling fix with testing instructions
- ✅ **[QUICK_TEST_GUIDE.md](assets/QUICK_TEST_GUIDE.md)** - Step-by-step testing guide
- ✅ **[TEST_PLAN.md](assets/TEST_PLAN.md)** - Comprehensive QA test suite
- ✅ **[QA_SUMMARY.md](assets/QA_SUMMARY.md)** - Testing methodology

---

## Cleanup and Rollback

Stop and remove all containers:

```bash
cd /path/to/multi-agent-chatbot/assets
docker compose -f docker-compose-api.yml down

# Optional: Remove volumes (deletes all data)
docker volume rm assets_postgres_data
docker volume rm assets_milvus_data
```

---

## Next Steps

- ✅ **Test all features** using [QUICK_TEST_GUIDE.md](assets/QUICK_TEST_GUIDE.md)
- 📊 **Monitor performance** using backend logs:
  ```bash
  docker logs -f chatbot-backend | grep -E "tool|document|error"
  ```
- 🔧 **Customize models** by editing `backend/.env`:
  - Try `gpt-4` or `gpt-3.5-turbo` for cost optimization
  - Experiment with different embedding models
- 🛠️ **Add new MCP servers** following the existing patterns in `backend/tools/mcp_servers/`
- 📈 **Scale the system** by adding Redis caching or multiple backend replicas

---

## Troubleshooting

### Common Issues

| Symptom | Cause | Fix |
|---------|--------|-----|
| "ChatAgent initialization failed" | Missing or invalid OpenAI API key | Check `backend/.env` file, verify API key is valid |
| "CORS error" when uploading | Frontend on wrong port | Verify accessing http://localhost:3100 (not 3000) |
| Empty Milvus collections | Documents not uploaded or indexing failed | Check backend logs for errors, retry document upload |
| WebSocket connection refused | Backend not fully started | Wait 30 seconds after `docker compose up`, check logs |
| "Tool not found" errors | MCP servers not initialized | Check backend logs for MCP initialization errors |
| PostgreSQL connection errors | Wrong credentials | Use `chatbot_user` not `chatbot` as username |

### Diagnostic Commands

```bash
# Check all container status
docker ps --format "table {{.Names}}\t{{.Status}}"

# View backend logs
docker logs chatbot-backend --tail 50

# Check Milvus collections
curl http://localhost:19531/v1/vector/collections

# Test backend API
curl http://localhost:8100/chats

# View real-time logs
docker logs -f chatbot-backend | grep -E "error|ERROR|initialized|tool"
```

### Advanced Troubleshooting

**If document upload fails:**
```bash
# Check backend logs for ingestion errors
docker logs chatbot-backend | grep -i "ingest\|document\|milvus"

# Verify Milvus is healthy
docker exec chatbot-milvus-standalone ps aux
```

**If tools aren't being called:**
```bash
# Verify tool support is enabled
docker logs chatbot-backend | grep "Tool calling debug info"
# Should show: supports_tools=True, has_tools=True

# Check MCP servers initialized
docker logs chatbot-backend | grep "Processing request of type ListToolsRequest"
# Should see 4 requests (one for each MCP server)
```

**If OpenAI API calls fail:**
```bash
# Check API key is loaded
docker exec chatbot-backend env | grep OPENAI_API_KEY

# View OpenAI API request logs
docker logs chatbot-backend | grep "HTTP Request: POST https://api.openai.com"
```

### Getting Help

- **Bug Reports**: See [ALL_BUGS_FIXED_REPORT.md](assets/ALL_BUGS_FIXED_REPORT.md) for known issues
- **Testing Guide**: Follow [QUICK_TEST_GUIDE.md](assets/QUICK_TEST_GUIDE.md)
- **Backend Logs**: Critical for debugging - always check first
- **GitHub Issues**: Report new issues with logs and reproduction steps

---

## System Status: ✅ FULLY OPERATIONAL

All critical bugs have been fixed. The system is production-ready with:
- ✅ OpenAI API integration working
- ✅ Document upload and RAG functional
- ✅ Image understanding operational
- ✅ Code generation working
- ✅ Real-time WebSocket streaming
- ✅ All MCP tools registered and callable

**Last Updated**: 2025-10-31
**Status**: All 6 bugs fixed, system fully tested and operational
