# QA Testing Summary - Multi-Agent Chatbot
**Date**: 2025-10-30
**Status**: READY FOR TESTING
**Test Framework**: Playwright-based (Manual + Automated via MCP)

---

## Executive Summary

✅ **All deployment issues have been resolved:**
1. ✅ MCP Server Environment Variables - Fixed (dotenv loading with explicit paths)
2. ✅ WebSocket Port Configuration - Fixed (8100 in QuerySection.tsx)
3. ✅ All 6 containers running and healthy
4. ✅ Backend ChatAgent initialized with OpenAI API
5. ✅ Comprehensive test plan created following Playwright best practices

---

## Test Infrastructure

### Completed Setup
- [TEST_PLAN.md](TEST_PLAN.md) - Comprehensive 15-test suite with Playwright methodology
- [TEST_RESULTS.md](TEST_RESULTS.md) - Ready for test execution logging
- Browser Automation MCP Server created (browser_automation.py) - **Pending Playwright installation**

### Test Categories
- **P0 Critical (4 tests)**: Basic Chat, Code Generation, Image Understanding, RAG
- **P1 High Priority (5 tests)**: Chat management, model switching
- **P2 Medium Priority (3 tests)**: Multi-doc RAG, source filtering
- **P3 Low Priority (3 tests)**: Error handling, performance, security

---

## Current Status - Ready for Manual Testing

### Why Manual Testing Now
While we created a browser automation MCP server, Playwright installation requires rebuilding the backend container. Given that:
1. All services are currently running and healthy
2. The primary deployment issues are fixed
3. Manual testing can begin immediately
4. Automated testing can be added later for CI/CD

**Recommendation**: Proceed with manual testing first to validate core functionality.

---

## TEST EXECUTION GUIDE

### Pre-Test Verification ✅

All systems ready:
```bash
✅ Backend: http://localhost:8100 (ChatAgent initialized)
✅ Frontend: http://localhost:3100 (WebSocket configured for port 8100)
✅ PostgreSQL: Healthy on port 5433
✅ Milvus: Healthy on port 19531
✅ OpenAI API: Configured (gpt-4-turbo, text-embedding-3-large)
✅ MCP Servers: code_generation, image_understanding, RAG (initialized)
```

---

### Critical Test Sequence (Execute in Order)

#### TEST 1: Basic Chat Functionality ⭐ **START HERE**

**Objective**: Verify WebSocket communication and OpenAI API integration

**Steps**:
1. Open http://localhost:3100
2. Verify UI loads completely:
   - Sidebar visible with "New Chat" button
   - Welcome message displayed
   - 4 agent cards visible (Search Documents, Image Processor, Code Generation, Chat)
   - Input textarea present and enabled
   - Send button (→) visible

3. Send test message:
   ```
   Hello! Can you introduce yourself and explain what you can do?
   ```

4. **Monitor in Terminal**:
   ```bash
   docker logs -f chatbot-backend | grep -i "websocket\|streaming\|error"
   ```

5. **Expected Observations**:
   - Loading indicator (three dots) appears immediately
   - Backend logs show:
     ```
     INFO: WebSocket connection established for chat_id: ...
     INFO: Sending history with 0 messages
     INFO: Streaming response...
     ```
   - Response streams token-by-token (NOT all at once)
   - Complete response appears within 10 seconds
   - Response mentions chatbot capabilities

6. **Success Criteria**:
   - ✅ No connection errors
   - ✅ Token streaming visible
   - ✅ Response is coherent
   - ✅ No JavaScript errors in browser console (F12)

**If this test FAILS**: Stop and report the issue immediately. All other tests depend on basic chat working.

---

#### TEST 2: Code Generation ⭐

**Prerequisites**: TEST 1 passed

**Steps**:
1. In the same chat, send:
   ```
   Write a Python function to calculate the nth Fibonacci number using recursion with memoization
   ```

2. **Monitor Backend**:
   ```bash
   docker logs -f chatbot-backend | grep -i "tool\|mcp"
   ```

3. **Expected Observations**:
   - Backend logs show: `INFO: Tool called: code_generation`
   - Code block rendered with syntax highlighting
   - Function includes:
     - Proper function definition
     - Recursion implementation
     - Memoization (decorator or cache dict)
     - Docstring/comments

4. **Success Criteria**:
   - ✅ Code is syntactically valid Python
   - ✅ Code solves the problem correctly
   - ✅ MCP tool was called
   - ✅ Response time < 15 seconds

---

#### TEST 3: Image Understanding ⭐

**Prerequisites**: TEST 1 passed

**Steps**:
1. Send message with image URL:
   ```
   Describe this image in detail: https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg
   ```

2. **Expected Observations**:
   - Backend logs: `INFO: Tool called: image_understanding`
   - Description mentions:
     - Animal type (cat)
     - Colors (orange/white/tabby)
     - Environment details
     - At least 3 specific visual details

3. **Success Criteria**:
   - ✅ Description accuracy ≥ 80%
   - ✅ Vision API was called
   - ✅ Response time < 20 seconds

4. **Database Verification** (optional):
   ```bash
   docker exec chatbot-postgres psql -U chatbot -d chatbot -c \
     "SELECT image_id, created_at, expires_at FROM images ORDER BY created_at DESC LIMIT 1;"
   ```
   Should show the image stored with 1-hour expiry.

---

#### TEST 4: Document Upload & RAG ⭐

**Prerequisites**: TEST 1 passed + test PDF file ready

**Preparation**:
- Create a simple 1-2 page PDF about any topic (e.g., save a Wikipedia article as PDF)
- Save to Downloads or Desktop for easy access

**Steps**:
1. Click "Upload Documents" button in sidebar (📁 icon or similar)
2. Select your test PDF
3. Wait for upload confirmation
4. Verify document appears in "Select Sources" dropdown
5. Select the document in dropdown
6. Send query:
   ```
   What is this document about? Provide a summary with key points.
   ```

7. **Expected Observations**:
   - Backend logs show:
     ```
     INFO: Document upload started
     INFO: Processing document with unstructured
     INFO: Embedding chunks with OpenAI
     INFO: Indexing in Milvus collection 'context'
     INFO: RAG query received
     INFO: Retrieved 8 chunks from Milvus
     ```
   - Response includes:
     - Summary of document content
     - Key points as bullet list
     - Citations or references to document sections

8. **Follow-up Query**:
   ```
   What are the specific details mentioned about [topic from document]?
   ```

9. **Success Criteria**:
   - ✅ Upload completes < 30 seconds
   - ✅ Summary accuracy ≥ 85%
   - ✅ Citations present
   - ✅ Follow-up retrieves correct info

---

## Monitoring Commands

### Real-time Logs
```bash
# All backend activity
docker logs -f chatbot-backend

# WebSocket specific
docker logs -f chatbot-backend | grep -i "websocket"

# Tool calls and MCP
docker logs -f chatbot-backend | grep -i "tool\|mcp"

# Errors only
docker logs -f chatbot-backend | grep -i "error\|failed"

# Frontend logs
docker logs -f chatbot-frontend
```

### Container Health
```bash
# Check all containers
docker compose -f /Users/dafesmith/Documents/multi-agent-chatbot/assets/docker-compose-api.yml ps

# Resource usage
docker stats chatbot-backend chatbot-frontend chatbot-postgres chatbot-milvus-standalone
```

### Database Queries
```bash
# Check conversations
docker exec chatbot-postgres psql -U chatbot -d chatbot -c \
  "SELECT chat_id, message_count, created_at FROM conversations ORDER BY created_at DESC;"

# Check images
docker exec chatbot-postgres psql -U chatbot -d chatbot -c \
  "SELECT image_id, created_at, expires_at FROM images ORDER BY created_at DESC;"
```

### API Health Checks
```bash
# Selected model
curl http://localhost:8100/selected_model

# Available models
curl http://localhost:8100/available_models

# Chat list
curl http://localhost:8100/chats

# Backend API docs
open http://localhost:8100/docs
```

---

## Issue Reporting Template

If any test fails, please provide:

```markdown
### ISSUE: [Brief Title]
**Test Case**: TEST [NUMBER]
**Priority**: P0/P1/P2/P3
**Status**: Blocking/Non-blocking

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
...

**Expected Result**:
[What should happen]

**Actual Result**:
[What actually happened]

**Evidence**:
- Browser Console: [Any errors - press F12]
- Backend Logs: [Paste relevant logs]
- Screenshot: [If applicable]

**Impact**:
[How this affects users]
```

---

## Additional Tests (After Critical Tests Pass)

### TEST 5: Chat History Loading
1. Refresh browser (F5)
2. Verify all messages reload
3. Send new message
4. Verify it appends correctly

### TEST 6: Create New Chat
1. Click "New Chat" button
2. Verify new empty chat session
3. Send test message
4. Switch back to original chat
5. Verify original history intact

### TEST 7: Rename Chat
1. Hover over chat in sidebar
2. Click rename icon
3. Enter new name
4. Verify persists after refresh

### TEST 8: Delete Chat
1. Create test chat
2. Click delete icon
3. Confirm deletion
4. Verify removed and doesn't reappear after refresh

### TEST 9: Model Switching
1. Click model dropdown
2. Select "gpt-3.5-turbo"
3. Send message
4. Note faster response
5. Switch back to "gpt-4-turbo"
6. Compare response quality

---

## Test Coverage Summary

| Component | Tested By | Status |
|-----------|-----------|--------|
| WebSocket Communication | TEST 1 | Pending |
| OpenAI Chat API | TEST 1 | Pending |
| MCP Code Generation | TEST 2 | Pending |
| MCP Image Understanding | TEST 3 | Pending |
| MCP RAG | TEST 4 | Pending |
| Document Upload | TEST 4 | Pending |
| Milvus Vector Search | TEST 4 | Pending |
| PostgreSQL Storage | TEST 1, 5 | Pending |
| Chat Management | TEST 6-8 | Pending |
| Model Switching | TEST 9 | Pending |

---

## Success Metrics

### Minimum for "PASS"
- ✅ All 4 P0 tests pass
- ✅ No critical errors
- ✅ WebSocket communication stable
- ✅ Token streaming works
- ✅ At least 1 MCP tool works

### Ideal for "PRODUCTION READY"
- ✅ All P0 + P1 tests pass (9 total)
- ✅ Performance within limits
- ✅ No data loss or corruption
- ✅ Error handling graceful

---

## Next Steps

1. **Execute TEST 1-4** (Critical path)
2. **Report any issues** using the template above
3. **If all critical tests pass**: Proceed with TEST 5-9
4. **Document results** in [TEST_RESULTS.md](TEST_RESULTS.md)
5. **Send findings** to development team

---

## Files Reference

- **[TEST_PLAN.md](TEST_PLAN.md)** - Detailed test methodology and all 15 test cases
- **[TEST_RESULTS.md](TEST_RESULTS.md)** - Live test execution log
- **[QA.md](QA.md)** - Original QA documentation with full test descriptions

---

## Automated Testing (Future Enhancement)

**Browser Automation MCP Server** created at:
- `backend/tools/mcp_servers/browser_automation.py`

**Capabilities** (once Playwright installed):
- Automated UI testing
- Screenshot capture
- Element interaction
- JavaScript execution
- Network monitoring

**To Enable**:
1. Add Playwright to Docker container
2. Install browser binaries
3. Restart backend
4. Use MCP tools for automated testing

---

**Status**: ✅ READY FOR MANUAL TESTING
**Blocker**: None
**Recommendation**: Start with TEST 1 immediately

Happy testing! 🚀
