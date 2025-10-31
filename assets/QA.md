# QA Testing & Validation Plan

## Project: Multi-Agent Chatbot API Deployment
**Test Environment:** Development
**Base URL:** http://localhost:3100
**API Docs:** http://localhost:8100/docs
**Date:** 2025-10-30

---

## 🎯 TESTING OBJECTIVES

1. Verify all core functionality works with OpenAI API integration
2. Validate port changes don't affect functionality
3. Ensure data persistence across container restarts
4. Confirm cost monitoring and API rate limits
5. Test error handling and edge cases

---

## ✅ PRE-TEST CHECKLIST

Before starting tests, verify:

- [ ] All containers are running and healthy
  ```bash
  docker compose -f docker-compose-api.yml ps
  ```
- [ ] Frontend accessible at http://localhost:3100
- [ ] Backend API docs at http://localhost:8100/docs
- [ ] OpenAI API key configured correctly
- [ ] No errors in backend logs:
  ```bash
  docker logs chatbot-backend | grep -i error
  ```

---

## 🧪 TEST SUITE

### TEST 1: Basic Chat Functionality ⭐ CRITICAL

**Objective:** Verify core chat functionality with OpenAI API

**Test Steps:**
1. Open http://localhost:3100 in browser
2. Verify welcome screen displays with sample prompts
3. Type: "Hello! Can you introduce yourself?"
4. Click send or press Enter

**Expected Results:**
- ✅ Message appears in chat interface
- ✅ Typing indicator shows while loading
- ✅ GPT-4 responds with coherent introduction
- ✅ Response streams token-by-token (not all at once)
- ✅ Response includes markdown formatting if applicable
- ✅ No error messages displayed

**Pass Criteria:**
- Response received within 5 seconds
- Response is contextually appropriate
- No console errors in browser dev tools

**Test Data:**
```
Input: "Hello! Can you introduce yourself?"
Expected: Introduction mentioning AI assistant capabilities
```

**Failure Scenarios:**
- ❌ "Invalid API key" error → Check .env file
- ❌ "Connection refused" → Backend container not running
- ❌ Timeout → Check OpenAI API status

---

### TEST 2: Code Generation ⭐ CRITICAL

**Objective:** Verify code generation tool integration

**Test Steps:**
1. Type: "Write a Python function to calculate the nth Fibonacci number"
2. Send message
3. Wait for response
4. Copy generated code
5. Verify syntax highlighting applied

**Expected Results:**
- ✅ Tool execution status shows "write_code" tool running
- ✅ Complete Python function generated
- ✅ Code includes:
  - Function definition
  - Parameter handling
  - Return statement
  - No markdown formatting (raw code)
- ✅ Syntax highlighting applied in UI
- ✅ Copy button available for code block

**Pass Criteria:**
- Code is syntactically correct
- Function solves the problem
- Response time < 10 seconds

**Test Data:**
```python
# Expected output format:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

**Additional Test Cases:**
| Language | Test Input | Expected Output |
|----------|-----------|-----------------|
| JavaScript | "Create a function to reverse a string" | Valid JS function |
| HTML | "Build a simple contact form" | Complete HTML form |
| Python | "Write a class for a binary search tree" | Complete class definition |

---

### TEST 3: Image Understanding ⭐ CRITICAL

**Objective:** Verify vision model integration

**Test Steps:**
1. Type: "Describe this image: https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/480px-Cat03.jpg"
2. Send message
3. Wait for tool execution
4. Review image description

**Expected Results:**
- ✅ Tool status shows "explain_image" executing
- ✅ Detailed description of image content
- ✅ Mentions: cat, animal, photograph
- ✅ Describes colors, setting, or details
- ✅ Response time < 15 seconds

**Pass Criteria:**
- Description is accurate
- Multiple details mentioned
- No hallucination of non-existent objects

**Additional Test Cases:**
| Image URL | Expected Description Elements |
|-----------|------------------------------|
| https://upload.wikimedia.org/wikipedia/commons/5/5b/Golden_Gate_Bridge_-_San_Francisco.jpg | Bridge, water, architecture |
| (Upload local image via UI) | Accurate description of uploaded image |

---

### TEST 4: Document Upload & RAG ⭐ CRITICAL

**Objective:** Verify document ingestion and retrieval

**Test Steps:**
1. Click "Upload Documents" button in sidebar
2. Select a PDF file (test-document.pdf)
3. Wait for upload to complete
4. Verify document appears in "Select Sources" dropdown
5. Check the document checkbox
6. Type: "What is this document about?"
7. Send message

**Expected Results:**
- ✅ Upload progress bar shown
- ✅ Success message after upload
- ✅ Document appears in sources list
- ✅ Tool status shows "search_documents" executing
- ✅ Response includes content from uploaded document
- ✅ Response cites relevant sections
- ✅ Hallucination check: Answer only from document, not general knowledge

**Pass Criteria:**
- Document indexed within 30 seconds
- Search results relevant to query
- Answer grounded in document content

**Test Documents:**
- Small PDF (< 1MB): Quick test
- Large PDF (> 5MB): Stress test
- Multi-page PDF: Pagination test

---

### TEST 5: Chat History Management

**Objective:** Verify conversation persistence

**Test Steps:**
1. Send message: "Remember this: my favorite color is blue"
2. Send message: "What's my favorite color?"
3. Click "New Chat" button
4. Send message: "What's my favorite color?"
5. Navigate back to previous chat via sidebar
6. Verify conversation history restored

**Expected Results:**
- ✅ AI remembers information within same chat
- ✅ AI doesn't remember in new chat (isolated context)
- ✅ Previous chats listed in sidebar
- ✅ Clicking previous chat loads full history
- ✅ Messages persist after page refresh

**Pass Criteria:**
- Memory works within conversation
- Chats are isolated from each other
- History loads in < 2 seconds

---

### TEST 6: Chat Renaming & Deletion

**Objective:** Verify chat management features

**Test Steps:**
1. Create new chat
2. Send test message
3. Hover over chat in sidebar
4. Click rename icon
5. Enter new name: "Test Chat"
6. Verify name updated
7. Click delete icon
8. Confirm deletion
9. Verify chat removed from list

**Expected Results:**
- ✅ Rename modal appears
- ✅ Name updates immediately
- ✅ Deletion confirmation shown
- ✅ Chat removed from sidebar
- ✅ Cannot navigate to deleted chat

---

### TEST 7: Model Switching

**Objective:** Verify ability to change models

**Test Steps:**
1. Open "Model Selection" in sidebar
2. Note current model (gpt-4-turbo)
3. Switch to gpt-3.5-turbo
4. Send test message
5. Verify response quality (faster, potentially lower quality)
6. Switch back to gpt-4-turbo

**Expected Results:**
- ✅ Model dropdown shows available models
- ✅ Selection persists across messages
- ✅ gpt-3.5-turbo responses faster but simpler
- ✅ gpt-4-turbo responses slower but higher quality

---

### TEST 8: Source Filtering (RAG)

**Objective:** Verify selective document retrieval

**Test Steps:**
1. Upload two different PDFs
2. Select only one document in "Select Sources"
3. Ask question about content in SELECTED document
4. Verify answer from selected document
5. Ask question about content in UNSELECTED document
6. Verify "No information found" or general response

**Expected Results:**
- ✅ Only selected documents used for retrieval
- ✅ Unselected documents ignored
- ✅ Clear indication when no relevant info found

---

### TEST 9: Concurrent Requests

**Objective:** Test system under load

**Test Steps:**
1. Open 3 browser tabs to http://localhost:3100
2. In each tab, send different messages simultaneously
3. Verify all responses complete successfully
4. Check for errors or timeouts

**Expected Results:**
- ✅ All requests handled
- ✅ No cross-contamination between chats
- ✅ Response times reasonable (< 30s each)

---

### TEST 10: Error Handling

**Objective:** Verify graceful error handling

**Test Cases:**

#### 10a. Invalid Image URL
```
Input: "Describe this image: https://invalid-url.com/nonexistent.jpg"
Expected: Error message explaining image not accessible
```

#### 10b. Empty Message
```
Input: (click send with empty text box)
Expected: Send button disabled or validation message
```

#### 10c. Very Long Message
```
Input: (paste 10,000+ character text)
Expected: Either accept or show character limit warning
```

#### 10d. Special Characters
```
Input: "Test <script>alert('xss')</script> message"
Expected: Text escaped, no script execution
```

#### 10e. API Rate Limit (Simulated)
```
Input: Send 20 messages rapid-fire
Expected: Queued or rate limit error message
```

---

### TEST 11: Streaming Behavior

**Objective:** Verify token streaming works correctly

**Test Steps:**
1. Send message: "Write a 500-word essay about AI"
2. Watch response appear
3. Verify tokens stream incrementally
4. Try to cancel mid-stream
5. Verify cancellation works

**Expected Results:**
- ✅ Tokens appear word-by-word (not sentence-by-sentence)
- ✅ Auto-scroll follows new content
- ✅ Cancel button stops generation
- ✅ Partial response saved to history

---

### TEST 12: Dark Mode / Theme Toggle

**Objective:** Verify UI theme switching

**Test Steps:**
1. Click theme toggle button
2. Verify dark mode applied
3. Toggle back to light mode
4. Refresh page
5. Verify theme preference persisted

**Expected Results:**
- ✅ All UI elements update colors
- ✅ Code syntax highlighting adapts to theme
- ✅ Theme persists across page reloads

---

### TEST 13: Mobile Responsiveness

**Objective:** Verify mobile UI functionality

**Test Steps:**
1. Open http://localhost:3100 on mobile device or responsive mode
2. Toggle sidebar
3. Send message
4. Upload document
5. Navigate between chats

**Expected Results:**
- ✅ Sidebar collapses to overlay on mobile
- ✅ All features accessible
- ✅ Text readable without zooming
- ✅ Buttons appropriately sized for touch

---

### TEST 14: WebSocket Reconnection

**Objective:** Verify connection resilience

**Test Steps:**
1. Open browser dev tools → Network tab
2. Start sending a message
3. Disable network mid-response
4. Re-enable network
5. Verify connection recovers

**Expected Results:**
- ✅ Error message shown when disconnected
- ✅ Automatic reconnection attempt
- ✅ Previous messages preserved
- ✅ Can resume chatting after reconnection

---

### TEST 15: Cost Monitoring

**Objective:** Verify API usage tracking

**Test Steps:**
1. Note OpenAI API usage before testing
2. Run tests 1-4 (10 messages total)
3. Check OpenAI dashboard: https://platform.openai.com/usage
4. Calculate expected cost
5. Verify usage logged correctly

**Expected Results:**
- ✅ Token usage increases in dashboard
- ✅ Cost aligns with expected (~$0.10-0.50 for 10 messages)
- ✅ Request counts match sent messages

**Cost Benchmarks:**
| Test | Estimated Tokens | Estimated Cost |
|------|-----------------|----------------|
| Basic chat (10 msgs) | ~2000 | ~$0.06 |
| Code generation (5 calls) | ~3000 | ~$0.09 |
| Image understanding (3 imgs) | ~1500 | ~$0.03 |
| RAG queries (10 searches) | ~4000 | ~$0.14 |

---

## 🔍 REGRESSION TESTING

### After Any Code Changes:

- [ ] Re-run all Critical (⭐) tests
- [ ] Verify no new errors in logs
- [ ] Check performance hasn't degraded

---

## 📊 TEST RESULTS TEMPLATE

### Test Execution Log

| Test ID | Test Name | Status | Time (s) | Notes |
|---------|-----------|--------|----------|-------|
| TEST-1 | Basic Chat | ⏳ | - | - |
| TEST-2 | Code Generation | ⏳ | - | - |
| TEST-3 | Image Understanding | ⏳ | - | - |
| TEST-4 | Document RAG | ⏳ | - | - |
| TEST-5 | Chat History | ⏳ | - | - |
| TEST-6 | Rename/Delete | ⏳ | - | - |
| TEST-7 | Model Switching | ⏳ | - | - |
| TEST-8 | Source Filtering | ⏳ | - | - |
| TEST-9 | Concurrent Requests | ⏳ | - | - |
| TEST-10 | Error Handling | ⏳ | - | - |
| TEST-11 | Streaming | ⏳ | - | - |
| TEST-12 | Theme Toggle | ⏳ | - | - |
| TEST-13 | Mobile UI | ⏳ | - | - |
| TEST-14 | Reconnection | ⏳ | - | - |
| TEST-15 | Cost Monitoring | ⏳ | - | - |

**Legend:**
- ⏳ Pending
- ✅ Passed
- ❌ Failed
- ⚠️ Partial Pass
- 🔄 Blocked/Skipped

---

## 🐛 BUG REPORT TEMPLATE

```markdown
**Bug ID:** BUG-XXX
**Test Case:** TEST-X
**Severity:** Critical / High / Medium / Low
**Priority:** P0 / P1 / P2 / P3

**Description:**
[Clear description of the bug]

**Steps to Reproduce:**
1. Step 1
2. Step 2
3. Step 3

**Expected Result:**
[What should happen]

**Actual Result:**
[What actually happened]

**Screenshots/Logs:**
[Attach relevant screenshots or log snippets]

**Environment:**
- Browser: Chrome 120
- OS: macOS
- Backend Container: chatbot-backend
- Logs:
```
docker logs chatbot-backend | grep ERROR
```

**Workaround:**
[If applicable]

**Assigned To:**
[Developer name]
```

---

## 🎯 TEST COMPLETION CRITERIA

### All Tests Pass When:

- ✅ 15/15 test cases pass
- ✅ No critical or high severity bugs
- ✅ All containers healthy
- ✅ API costs within expected range
- ✅ No data loss observed
- ✅ Performance meets benchmarks:
  - Chat response: < 5s
  - Code generation: < 10s
  - Image analysis: < 15s
  - Document upload: < 30s

---

## 📈 PERFORMANCE BENCHMARKS

### Response Time Targets:

| Feature | Target | Acceptable | Unacceptable |
|---------|--------|-----------|--------------|
| Basic chat | < 3s | < 5s | > 10s |
| Code generation | < 8s | < 15s | > 30s |
| Image understanding | < 10s | < 20s | > 40s |
| Document search | < 4s | < 8s | > 15s |
| Upload small PDF | < 10s | < 30s | > 60s |
| Upload large PDF | < 30s | < 60s | > 120s |

---

## 🔧 DEBUGGING GUIDE

### Common Issues:

**Issue: Frontend not loading**
```bash
# Check frontend container
docker logs chatbot-frontend | tail -n 50

# Verify port mapping
lsof -i :3100

# Restart frontend
docker restart chatbot-frontend
```

**Issue: Backend API errors**
```bash
# Check backend logs
docker logs chatbot-backend | grep -i "error\|exception"

# Verify environment variables
docker exec chatbot-backend env | grep OPENAI

# Test API directly
curl http://localhost:8100/docs
```

**Issue: OpenAI API failures**
```bash
# Check API key
cat backend/.env | grep OPENAI_API_KEY

# Test API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Check rate limits
# Visit: https://platform.openai.com/usage
```

**Issue: Database connection errors**
```bash
# Check PostgreSQL
docker exec -it chatbot-postgres psql -U chatbot_user -d chatbot -c "SELECT 1;"

# Check Milvus
docker exec -it chatbot-milvus-standalone curl http://localhost:9091/healthz
```

---

## 📞 ESCALATION CONTACTS

**Critical Issues:** dafesmith
**OpenAI API Issues:** https://help.openai.com
**Docker Issues:** DevOps team
**Database Issues:** DBA team

---

## ✅ SIGN-OFF

### QA Team Sign-Off:

- **Tested By:** ___________________
- **Date:** ___________________
- **Result:** Pass / Fail / Conditional Pass
- **Notes:** ___________________

### Dev Team Sign-Off:

- **Reviewed By:** ___________________
- **Date:** ___________________
- **Approved:** Yes / No
- **Comments:** ___________________

---

*Last Updated: 2025-10-30 23:00 UTC*
*Version: 1.0*
