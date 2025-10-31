# Deployment Task List

## Project: Multi-Agent Chatbot API Deployment
**Date:** 2025-10-30
**Environment:** Development
**Deploy Type:** API-based (OpenAI)

---

## ✅ PRE-DEPLOYMENT TASKS

### 1. Port Conflict Resolution
- [x] Check ports 3000, 8000, 5432, 19530 for conflicts
- [x] **CONFLICT FOUND:** Ports 3000 and 8000 in use by nat-ui and nat-backend
- [x] **RESOLUTION:** Updated ports to avoid conflicts:
  - Frontend: `3000` → `3100`
  - Backend: `8000` → `8100`
  - PostgreSQL: `5432` → `5433`
  - Milvus: `19530` → `19531`, `9091` → `9092`

### 2. Code Updates for API Integration
- [x] Update `backend/agent.py` (lines 155-171)
  - Changed from local model endpoint to OpenAI API
  - Added `os.getenv()` for API key and base URL

- [x] Update `backend/vector_store.py` (lines 32-79)
  - Removed `CustomEmbeddings` class (local qwen3-embedding)
  - Integrated `OpenAIEmbeddings` with `text-embedding-3-large`

- [x] Update `backend/tools/mcp_servers/code_generation.py` (lines 26-47)
  - Changed from local deepseek-coder to OpenAI API
  - Model: `gpt-4-turbo`

- [x] Update `backend/tools/mcp_servers/image_understanding.py` (lines 45-50)
  - Changed from local Qwen2.5-VL to OpenAI Vision
  - Model: `gpt-4-turbo` (with vision)

### 3. Configuration Files
- [x] Create `backend/.env` with OpenAI API key
  - API Key: `sk-proj-Qw7r...alsMA` (configured)
  - Models: gpt-4-turbo, text-embedding-3-large

- [x] Update `docker-compose-api.yml`
  - Updated all container names to avoid conflicts
  - Updated port mappings
  - Added health check dependencies

---

## 🚀 DEPLOYMENT TASKS

### 4. Docker Build & Deploy
- [x] Navigate to project directory
- [x] Stop old containers (if running)
- [x] Build and start new containers: `docker compose -f docker-compose-api.yml up -d --build`
  - **Status:** In progress (building)
  - Backend: Building Python dependencies
  - Frontend: Building Node.js dependencies
  - PostgreSQL: Pulling image
  - Milvus: Pulling image
  - etcd: Pulling image
  - minio: Pulling image

---

## 🔍 POST-DEPLOYMENT TASKS

### 5. Container Health Verification
- [ ] Check all containers are running
  ```bash
  docker compose -f docker-compose-api.yml ps
  ```
  - [ ] chatbot-backend (healthy)
  - [ ] chatbot-frontend (up)
  - [ ] chatbot-postgres (healthy)
  - [ ] chatbot-milvus-standalone (healthy)
  - [ ] chatbot-milvus-etcd (healthy)
  - [ ] chatbot-milvus-minio (healthy)

### 6. Service Logs Review
- [ ] Check backend logs for errors
  ```bash
  docker logs chatbot-backend | tail -n 50
  ```
  - [ ] Verify OpenAI API connection
  - [ ] Verify PostgreSQL connection
  - [ ] Verify Milvus connection
  - [ ] Verify MCP tools loaded

- [ ] Check frontend logs for errors
  ```bash
  docker logs chatbot-frontend | tail -n 30
  ```

### 7. Database Initialization
- [ ] Verify PostgreSQL tables created
  ```bash
  docker exec -it chatbot-postgres psql -U chatbot_user -d chatbot -c "\dt"
  ```
  - [ ] conversations table
  - [ ] chat_metadata table
  - [ ] images table

- [ ] Verify Milvus collection created
  ```bash
  docker logs chatbot-milvus-standalone | grep "context"
  ```

---

## 🧪 TESTING TASKS

### 8. Basic Connectivity Tests
- [ ] Access frontend UI: http://localhost:3100
- [ ] Backend API health: http://localhost:8100/docs
- [ ] WebSocket endpoint test

### 9. Functional Tests (See QA.md for detailed tests)
- [ ] Test 1: Basic chat functionality
- [ ] Test 2: Code generation
- [ ] Test 3: Image understanding
- [ ] Test 4: Document upload & RAG
- [ ] Test 5: Chat history management
- [ ] Test 6: Model switching
- [ ] Test 7: Error handling

---

## 📊 MONITORING TASKS

### 10. Performance Monitoring
- [ ] Monitor OpenAI API usage
  - Dashboard: https://platform.openai.com/usage
  - Check token consumption
  - Verify costs align with estimates

- [ ] Monitor container resources
  ```bash
  docker stats chatbot-backend chatbot-frontend chatbot-postgres chatbot-milvus-standalone
  ```

- [ ] Check log sizes
  ```bash
  docker logs chatbot-backend 2>&1 | wc -l
  ```

---

## 🔧 ROLLBACK PLAN

### 11. Rollback Procedures (if needed)
- [ ] Stop all containers
  ```bash
  docker compose -f docker-compose-api.yml down
  ```

- [ ] Remove volumes (if corrupted)
  ```bash
  docker volume rm assets_postgres_data
  docker volume rm assets_milvus_data
  ```

- [ ] Restore from backup (if available)

---

## 📝 DOCUMENTATION TASKS

### 12. Update Documentation
- [x] Create TASK.md (this file)
- [x] Create QA.md (testing plan)
- [x] Create DEPLOYMENT_SUMMARY.md
- [x] Create QUICK_START_API.md
- [x] Create API_DEPLOYMENT_GUIDE.md

### 13. Handoff to QA
- [ ] Provide QA team with:
  - [ ] URL: http://localhost:3100
  - [ ] QA.md testing plan
  - [ ] Access to Docker logs
  - [ ] OpenAI API usage dashboard access

---

## ⚠️ KNOWN ISSUES

1. **Port Conflicts**
   - Resolution: All ports updated to avoid conflicts
   - Frontend: 3100 (instead of 3000)
   - Backend: 8100 (instead of 8000)

2. **npm Vulnerabilities**
   - Frontend build shows 7 vulnerabilities (3 low, 4 moderate)
   - Action: Review with security team
   - Non-blocking for testing

---

## 🎯 SUCCESS CRITERIA

### Deployment is successful when:
- [ ] All 6 containers running and healthy
- [ ] Frontend accessible at http://localhost:3100
- [ ] Backend API docs accessible at http://localhost:8100/docs
- [ ] Basic chat functionality works
- [ ] OpenAI API calls successful
- [ ] PostgreSQL storing chat history
- [ ] Milvus vector search operational
- [ ] All QA tests pass

---

## 📞 CONTACTS

**Development Team:**
- Backend: dafesmith
- Frontend: dafesmith
- DevOps: dafesmith

**External Services:**
- OpenAI Support: https://help.openai.com
- OpenAI Status: https://status.openai.com

---

## 📅 TIMELINE

| Task | Start Time | Duration | Status |
|------|-----------|----------|--------|
| Port conflict check | 22:55 | 2 min | ✅ Complete |
| Code updates | 22:57 | 5 min | ✅ Complete |
| Docker build | 22:58 | 5-10 min | 🔄 In Progress |
| Health checks | TBD | 5 min | ⏳ Pending |
| QA testing | TBD | 30 min | ⏳ Pending |

**Estimated Total Time:** 45-60 minutes
**Started:** 2025-10-30 22:55 UTC
**Expected Completion:** 2025-10-30 23:40 UTC

---

*Last Updated: 2025-10-30 22:58 UTC*
