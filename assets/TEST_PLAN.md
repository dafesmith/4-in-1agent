# Multi-Agent Chatbot - QA Test Plan
**Version**: 1.0
**Date**: 2025-10-30
**Test Plan ID**: MAC-QA-2025-Q4
**Tester**: QA Agent (Automated)

## Test Objective
Ensure all functionalities of the multi-agent chatbot remain stable following OpenAI API integration, verify cross-component integration (Frontend ↔ Backend ↔ PostgreSQL ↔ Milvus), and validate critical user workflows for production readiness.

---

## Test Environment
- **Frontend URL**: http://localhost:3100
- **Backend API**: http://localhost:8100
- **Backend Docs**: http://localhost:8100/docs
- **WebSocket**: ws://localhost:8100/ws/chat/{chat_id}
- **Database**: PostgreSQL 15 (port 5433)
- **Vector Store**: Milvus v2.5.15 (port 19531)
- **LLM Provider**: OpenAI API (gpt-4-turbo, text-embedding-3-large)

### Service Status
- ✅ Backend Container: Running
- ✅ Frontend Container: Running
- ✅ PostgreSQL: Healthy
- ✅ Milvus: Healthy
- ✅ Etcd: Healthy
- ✅ Minio: Healthy

---

## Test Strategy (Playwright Best Practices)

### Principles
1. **User-Centric Testing**: Focus on user-visible behavior and workflows
2. **Test Isolation**: Each test runs independently with clean state
3. **Stable Locators**: Use role-based and user-facing attributes (avoid CSS selectors)
4. **Web-First Assertions**: Use auto-waiting assertions
5. **Critical Path First**: Prioritize business-critical functionality

### Test Categories
- **Critical Tests (P0)**: Must pass before deployment - Basic chat, Code gen, Image understanding, RAG
- **High Priority (P1)**: Important features - Chat management, model switching
- **Medium Priority (P2)**: Secondary features - Source filtering, performance
- **Low Priority (P3)**: Edge cases - Security, error handling

---

## Test Cases

### CRITICAL TESTS (P0) ⭐

#### TEST 1: Basic Chat Functionality
**Priority**: P0 - CRITICAL
**Type**: Integration Test
**Validates**: OpenAI API, WebSocket, Agent workflow, Token streaming

**Pre-conditions**:
- Frontend accessible at http://localhost:3100
- Backend ChatAgent initialized
- OpenAI API key configured

**Test Steps**:
1. Open http://localhost:3100 in browser
2. Verify chat interface loads (sidebar visible, input field present)
3. Locate input field using role: `getByRole('textbox')`
4. Type message: "Hello! Can you introduce yourself and explain what you can do?"
5. Click send button using role: `getByRole('button', { name: /send/i })`
6. Wait for loading indicator to appear
7. Wait for response to stream token-by-token
8. Verify response appears in chat history
9. Verify response contains relevant content about chatbot capabilities

**Expected Results**:
- ✅ Message sent successfully
- ✅ Loading indicator displays during processing
- ✅ Response streams incrementally (token streaming working)
- ✅ Complete response appears in chat
- ✅ Response is coherent and relevant
- ✅ Backend logs show: "WebSocket connection established", "Streaming response..."
- ✅ No errors in browser console or backend logs

**Acceptance Criteria**:
- Response received within 10 seconds
- Token streaming visible (not all-at-once)
- No connection errors

---

#### TEST 2: Code Generation
**Priority**: P0 - CRITICAL
**Type**: Functional Test
**Validates**: MCP code generation tool, Tool calling, GPT-4 integration

**Pre-conditions**:
- TEST 1 passed
- MCP code generation server initialized

**Test Steps**:
1. In same chat session, send message: "Write a Python function to calculate the nth Fibonacci number using recursion with memoization"
2. Wait for response
3. Verify response contains code block
4. Check code syntax highlighting is present
5. Verify code includes:
   - Function definition
   - Recursion implementation
   - Memoization (e.g., decorator or cache dict)
   - Proper indentation

**Expected Results**:
- ✅ Code block rendered with syntax highlighting
- ✅ Valid Python syntax
- ✅ Function solves the specified problem
- ✅ Memoization implemented correctly
- ✅ Includes docstring/comments (good practice)
- ✅ Backend logs show MCP tool call: "code_generation"

**Acceptance Criteria**:
- Code is executable
- Code follows Python best practices
- Response time < 15 seconds

---

#### TEST 3: Image Understanding
**Priority**: P0 - CRITICAL
**Type**: Functional Test
**Validates**: MCP image understanding tool, OpenAI Vision API, Image storage

**Pre-conditions**:
- TEST 1 passed
- MCP image understanding server initialized

**Test Steps**:
1. Send message with image URL: "Describe this image in detail: https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"
2. Wait for response (may take longer due to vision API)
3. Verify response describes image content
4. Check description mentions: animal type, colors, setting, details

**Expected Results**:
- ✅ Image processed successfully
- ✅ Description is accurate and detailed
- ✅ Mentions: cat, colors (orange/white), environment details
- ✅ Response demonstrates visual understanding
- ✅ Backend logs show MCP tool call: "image_understanding"
- ✅ Image stored in PostgreSQL images table with 1-hour expiry

**Acceptance Criteria**:
- Description accuracy ≥ 80%
- Includes at least 3 visual details
- Response time < 20 seconds

---

#### TEST 4: Document Upload & RAG
**Priority**: P0 - CRITICAL
**Type**: End-to-End Test
**Validates**: Document ingestion, Milvus vector store, OpenAI embeddings, RAG pipeline

**Pre-conditions**:
- TEST 1 passed
- Milvus healthy and accessible
- OpenAI embeddings API working

**Test Steps**:
1. Click "Upload Documents" button in sidebar
2. Upload test PDF file (prepare a small 1-2 page PDF about a specific topic)
3. Wait for upload success message
4. Verify document appears in "Select Sources" dropdown
5. Select the uploaded document in dropdown
6. Send message: "What is this document about? Provide a summary."
7. Wait for RAG response
8. Verify response references document content
9. Send follow-up: "What are the key points mentioned in section 2?"
10. Verify response cites specific content

**Expected Results**:
- ✅ File upload completes successfully
- ✅ Document appears in sources list
- ✅ Source selection updates UI state
- ✅ Summary is accurate and relevant
- ✅ Response includes citations/references
- ✅ Follow-up query retrieves correct section
- ✅ Backend logs show: document processing, Milvus indexing, retrieval query
- ✅ Milvus collection 'context' contains new vectors

**Acceptance Criteria**:
- Upload completes in < 30 seconds
- Summary accuracy ≥ 85%
- Citations present in response
- Retrieval precision ≥ 70%

---

### HIGH PRIORITY TESTS (P1)

#### TEST 5: Chat History Loading
**Priority**: P1
**Type**: Functional Test
**Validates**: PostgreSQL storage, Chat persistence, State management

**Test Steps**:
1. Complete TEST 1 (creates chat history)
2. Refresh browser page (F5)
3. Verify chat history loads automatically
4. Verify all previous messages visible
5. Verify message order preserved
6. Send new message
7. Verify new message appends correctly

**Expected Results**:
- ✅ Previous messages load on refresh
- ✅ Message order correct (chronological)
- ✅ No duplicate messages
- ✅ New messages append seamlessly

---

#### TEST 6: Create New Chat
**Priority**: P1
**Type**: Functional Test
**Validates**: Chat management, State isolation

**Test Steps**:
1. Click "New Chat" button
2. Verify new chat session created
3. Verify chat history is empty
4. Verify new chat_id generated
5. Send test message in new chat
6. Switch back to original chat
7. Verify original chat history intact

**Expected Results**:
- ✅ New chat has empty history
- ✅ Unique chat_id assigned
- ✅ Chat sessions isolated
- ✅ Switching preserves state

---

#### TEST 7: Rename Chat
**Priority**: P1
**Type**: Functional Test

**Test Steps**:
1. Hover over chat in sidebar
2. Click rename icon/button
3. Enter new name: "Test Chat - Renamed"
4. Press Enter or click confirm
5. Verify name updates in sidebar
6. Refresh page
7. Verify renamed chat persists

**Expected Results**:
- ✅ Chat name updates immediately
- ✅ Rename persists after refresh
- ✅ No data loss

---

#### TEST 8: Delete Chat
**Priority**: P1
**Type**: Functional Test

**Test Steps**:
1. Create new test chat
2. Send test message
3. Click delete icon/button
4. Confirm deletion
5. Verify chat removed from sidebar
6. Verify redirect to different chat or empty state
7. Refresh page
8. Verify deleted chat does not reappear

**Expected Results**:
- ✅ Chat deleted from UI
- ✅ Deletion persists
- ✅ Database record removed

---

### MEDIUM PRIORITY TESTS (P2)

#### TEST 9: Model Switching
**Priority**: P2
**Type**: Configuration Test

**Test Steps**:
1. Check current model (should be gpt-4-turbo)
2. Click model selector dropdown
3. Select "gpt-3.5-turbo"
4. Send test message: "What model are you?"
5. Verify response generated (faster than GPT-4)
6. Switch back to gpt-4-turbo
7. Send same message
8. Compare response quality

**Expected Results**:
- ✅ Model switch successful
- ✅ Both models generate responses
- ✅ GPT-3.5 faster than GPT-4
- ✅ GPT-4 response more detailed

---

#### TEST 10: Multi-Document RAG
**Priority**: P2
**Type**: Advanced Feature Test

**Test Steps**:
1. Upload 3 different PDF documents
2. Select all 3 in sources dropdown
3. Send query spanning multiple docs
4. Verify response synthesizes info from multiple sources
5. Check citations reference multiple documents

**Expected Results**:
- ✅ Multiple sources processed
- ✅ Cross-document synthesis
- ✅ Citations from multiple docs

---

#### TEST 11: Source Filtering
**Priority**: P2
**Type**: Functional Test

**Test Steps**:
1. With multiple documents uploaded
2. Select only one source
3. Send query
4. Verify response only uses selected source
5. Deselect all sources
6. Send query
7. Verify general response (no RAG)

**Expected Results**:
- ✅ Source filtering works
- ✅ RAG uses only selected sources
- ✅ No sources = no RAG retrieval

---

### LOW PRIORITY TESTS (P3)

#### TEST 12: Error Handling
**Priority**: P3
**Type**: Negative Test

**Test Steps**:
1. Disconnect internet/OpenAI API
2. Send message
3. Verify error message displayed
4. Verify graceful degradation (no crash)
5. Restore connection
6. Verify recovery

**Expected Results**:
- ✅ User-friendly error message
- ✅ No application crash
- ✅ Auto-recovery after reconnection

---

#### TEST 13: Token Streaming
**Priority**: P3
**Type**: Performance Test

**Test Steps**:
1. Send message requesting long response
2. Observe token streaming behavior
3. Measure time to first token
4. Verify incremental updates
5. Check for stream interruptions

**Expected Results**:
- ✅ First token < 2 seconds
- ✅ Smooth streaming (no stuttering)
- ✅ No stream drops

---

#### TEST 14: Long Conversation Performance
**Priority**: P3
**Type**: Performance Test

**Test Steps**:
1. Send 20+ messages in single chat
2. Monitor response times
3. Check memory usage
4. Verify no degradation
5. Test history loading speed

**Expected Results**:
- ✅ Response time stable
- ✅ No memory leaks
- ✅ History loads < 3 seconds

---

#### TEST 15: Security - API Key Validation
**Priority**: P3
**Type**: Security Test

**Test Steps**:
1. Check .env file permissions
2. Verify API key not exposed in frontend
3. Check browser network tab (no API key in requests)
4. Verify backend doesn't log API key
5. Test with invalid API key (if safe to do so)

**Expected Results**:
- ✅ API key never exposed to client
- ✅ Secure backend-only usage
- ✅ Invalid key shows proper error

---

## Test Execution Log

### Session Information
- **Test Date**: 2025-10-30
- **Environment**: Docker Compose (Local Development)
- **Browser**: To be determined during manual testing
- **OS**: macOS (Darwin 25.0.0)

### Test Results
Will be filled during test execution...

---

## Issue Tracking Template

### Issue Format
```
ISSUE-{NUMBER}: {TITLE}
Priority: P0/P1/P2/P3
Test Case: TEST {NUMBER}
Status: Open/In Progress/Resolved

Description:
{Detailed description of the issue}

Steps to Reproduce:
1. {Step 1}
2. {Step 2}
...

Expected Result:
{What should happen}

Actual Result:
{What actually happened}

Evidence:
- Screenshot: {path}
- Logs: {relevant logs}
- Network: {network activity}

Impact:
{User impact and severity}

Proposed Fix:
{Developer notes}
```

---

## Test Coverage Matrix

| Component | Coverage | Critical Tests |
|-----------|----------|----------------|
| Frontend UI | 100% | TEST 1, 6, 7, 8 |
| WebSocket | 100% | TEST 1 |
| OpenAI API | 100% | TEST 1, 2, 3 |
| MCP Servers | 100% | TEST 2, 3 |
| RAG Pipeline | 100% | TEST 4, 10, 11 |
| PostgreSQL | 100% | TEST 5, 7, 8 |
| Milvus | 100% | TEST 4, 10 |
| Error Handling | 80% | TEST 12 |
| Performance | 60% | TEST 13, 14 |
| Security | 40% | TEST 15 |

---

## Sign-Off Criteria

### Blocker Issues (Must Fix)
- No P0 test failures
- All critical workflows functional
- No data loss or corruption
- No security vulnerabilities

### Release Readiness
- ≥ 95% P0 test pass rate
- ≥ 85% P1 test pass rate
- All blockers resolved
- Performance within acceptable limits

---

## Notes
- This test plan follows Playwright best practices for locator strategies and test isolation
- Manual execution required due to Docker environment constraints
- Automated Playwright tests recommended for CI/CD pipeline
- Test data should be prepared before execution (sample PDFs, test images)
