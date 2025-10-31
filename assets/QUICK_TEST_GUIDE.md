# Quick Test Guide - Verify All Bug Fixes

**System Status**: 🟢 ALL BUGS FIXED - READY FOR TESTING

---

## What Was Fixed?

✅ **Bug #1**: Agent tool calling for OpenAI models (CRITICAL)
✅ **Bug #2**: RAG server API endpoint configuration (CRITICAL)
✅ **Bug #3**: Milvus collection memory loading (CRITICAL)
✅ **Bug #4**: Environment variable loading in RAG server
✅ **Bug #5**: PostgreSQL documentation clarification

---

## Quick System Check

```bash
# 1. Check all containers are running:
docker ps

# Expected: 6 containers running
# - chatbot-backend
# - chatbot-frontend
# - chatbot-postgres
# - chatbot-milvus-standalone
# - chatbot-milvus-etcd
# - chatbot-milvus-minio

# 2. Check backend is healthy:
docker logs chatbot-backend --tail 20

# Expected to see:
# ✅ "ChatAgent initialized successfully"
# ✅ "PostgreSQL storage initialized successfully"
# ✅ "Processing request of type ListToolsRequest"
```

---

## Test 1: Image Understanding ⭐ CRITICAL

**What to Test**: Verify the agent can analyze images using the `explain_image` tool

**Steps**:
1. Open http://localhost:3100
2. Send this message:
   ```
   Describe this image in detail: https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg
   ```

**Expected Result**:
- ✅ Detailed description of the image (orange cat, sitting, etc.)
- ✅ Response within 15-20 seconds
- ✅ No error messages

**Previous Behavior (BROKEN)**:
- ❌ "I'm unable to directly view or analyze images from URLs"

**Monitor Backend**:
```bash
docker logs -f chatbot-backend | grep -i "tool\|image"
```

**Success Criteria**:
- Backend logs show: `Executing tool...explain_image`
- Accurate image description returned
- No connection errors

---

## Test 2: Document RAG ⭐ CRITICAL

**What to Test**: Verify document upload, indexing, and retrieval with the `search_documents` tool

**Steps**:
1. **Prepare a test PDF** (1-2 pages)
   - Use any PDF with clear content
   - Example: A research paper abstract, product manual, etc.

2. **Upload document**:
   - Click "Upload Document" button
   - Select your PDF file
   - Wait for success message

3. **Select document**:
   - Open "Select Sources" dropdown
   - Select your uploaded document

4. **Query document**:
   ```
   What is this document about? Provide a detailed summary.
   ```

**Expected Result**:
- ✅ Summary based on actual document content
- ✅ Specific details from the PDF
- ✅ Response includes citations

**Previous Behavior (BROKEN)**:
- ❌ "I currently don't have the capability to view documents"

**Monitor Milvus Collection**:
```bash
# Before upload:
curl http://localhost:19531/v1/vector/collections
# Expected: {"code":200,"data":[]}

# After upload (wait 10 seconds):
curl http://localhost:19531/v1/vector/collections
# Expected: {"code":200,"data":[{"collectionName":"context",...}]}
```

**Monitor Backend**:
```bash
docker logs -f chatbot-backend | grep -i "document\|milvus\|collection"
```

**Success Criteria**:
- Document upload completes successfully
- Milvus collection "context" created and loaded
- Backend logs show: `Executing tool...search_documents`
- Accurate document summary returned
- Summary contains specific details from PDF

---

## Test 3: Code Generation ⭐ CRITICAL

**What to Test**: Verify the agent can generate code using the `write_code` tool

**Steps**:
1. Send this message:
   ```
   Write a Python function to calculate the nth Fibonacci number using recursion with memoization. Include docstring and type hints.
   ```

**Expected Result**:
- ✅ Complete Python function
- ✅ Memoization implemented (decorator or manual)
- ✅ Type hints included
- ✅ Docstring present

**Previous Behavior (BROKEN)**:
- ❌ Generic code without tool usage

**Success Criteria**:
- Backend logs show: `Executing tool...write_code`
- Valid Python syntax
- Memoization correctly implemented
- Professional code quality

---

## Test 4: Basic Chat (Already Working)

**What to Test**: Verify basic LLM responses without tools

**Steps**:
```
Hello! Can you introduce yourself and explain what capabilities you have?
```

**Expected Result**:
- ✅ Coherent response
- ✅ Lists available capabilities
- ✅ Response within 10 seconds

**Success Criteria**:
- Normal chat functionality works
- No connection errors
- Token streaming visible

---

## Troubleshooting

### If Image Understanding Doesn't Work:

1. Check backend logs:
   ```bash
   docker logs chatbot-backend --tail 50 | grep -i "explain_image\|vision\|openai"
   ```

2. Verify OPENAI_API_KEY is set:
   ```bash
   docker exec chatbot-backend env | grep OPENAI_API_KEY
   ```

3. Check MCP server status:
   ```bash
   docker logs chatbot-backend | grep "image-understanding-server"
   ```

### If Document RAG Doesn't Work:

1. Check if collection was created:
   ```bash
   curl http://localhost:19531/v1/vector/collections
   ```

2. Check document upload logs:
   ```bash
   docker logs chatbot-backend | grep -i "ingest\|index\|milvus"
   ```

3. Verify collection loaded:
   ```bash
   docker logs chatbot-backend | grep "Collection.*loaded into memory"
   ```

4. Check RAG MCP server:
   ```bash
   docker logs chatbot-backend | grep "rag-server\|search_documents"
   ```

### If All Tools Fail:

1. Check if tools are being passed to API:
   ```bash
   docker logs chatbot-backend | grep "Tool calling debug info"
   ```
   Should show: `supports_tools=True, has_tools=True`

2. Verify MCP servers initialized:
   ```bash
   docker logs chatbot-backend | grep "Processing request of type ListToolsRequest"
   ```
   Should see 4 requests (one for each MCP server)

3. Restart backend:
   ```bash
   cd /Users/dafesmith/Documents/multi-agent-chatbot/assets
   docker compose -f docker-compose-api.yml restart backend
   ```

---

## Expected System Behavior After Fixes

### Tool Calling Flow (Working Now)

```
User Request → Frontend → Backend WebSocket
    ↓
ChatAgent.query()
    ↓
ChatAgent.generate() with tools
    ↓
Tool support check → TRUE ✅ (was FALSE ❌)
    ↓
OpenAI API called WITH tools parameter ✅ (was without ❌)
    ↓
OpenAI returns tool call: {name: "explain_image", ...}
    ↓
ChatAgent.tool_node() executes tool
    ↓
MCP Server processes request
    ↓
Result returned to agent
    ↓
Response streamed to frontend
```

### Document RAG Flow (Working Now)

```
User uploads PDF → Backend /ingest endpoint
    ↓
VectorStore.index_documents()
    ↓
Documents split into chunks
    ↓
OpenAI embeddings generated
    ↓
Stored in Milvus collection "context"
    ↓
Collection flushed to disk ✅
    ↓
Collection loaded into memory ✅ (was missing ❌)
    ↓
User asks question → search_documents tool called
    ↓
RAG MCP server connects to OpenAI API ✅ (was broken ❌)
    ↓
Retrieves documents from loaded collection ✅
    ↓
Generates answer with context ✅
```

---

## Success Indicators

If all tests pass, you should see:

✅ **Image Understanding**: Accurate image descriptions
✅ **Document RAG**: Content-based summaries with citations
✅ **Code Generation**: Professional code with proper structure
✅ **Basic Chat**: Normal conversation flow
✅ **No Error Messages**: Clean execution logs
✅ **Fast Response Times**: <20 seconds for all queries

---

## Report Issues

If you encounter any problems:

1. **Capture Backend Logs**:
   ```bash
   docker logs chatbot-backend --tail 100 > backend_logs.txt
   ```

2. **Check Milvus Status**:
   ```bash
   curl http://localhost:19531/v1/vector/collections > milvus_status.txt
   ```

3. **Screenshot Error Messages**: From the frontend

4. **Note Exact Steps**: What you did, what you expected, what happened

---

## Documentation Files

- 📄 [ALL_BUGS_FIXED_REPORT.md](ALL_BUGS_FIXED_REPORT.md) - Complete technical details
- 📄 [CRITICAL_BUG_FIX_REPORT.md](CRITICAL_BUG_FIX_REPORT.md) - First fix (tool calling)
- 📄 [TEST_PLAN.md](TEST_PLAN.md) - Full QA test suite
- 📄 [QA_SUMMARY.md](QA_SUMMARY.md) - Testing methodology

---

**Ready to Test!** 🚀

All critical bugs are fixed. Start with Test 1 (Image Understanding) and work through the list.
