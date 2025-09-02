# SarvanOM Testing Instructions

## 🚀 Quick Start

### 1. Start All Services
Run the batch file to start all services:
```bash
start_services.bat
```

This will open separate command windows for:
- **API Gateway** (Port 8000)
- **Retrieval Service** (Port 8001) 
- **Frontend** (Port 3000)

### 2. Access the Application

#### Frontend Testing
- **Main App**: http://localhost:3000
- **Multimodal Demo**: http://localhost:3000/multimodal-demo
- **API Documentation**: http://localhost:8000/docs

#### Backend Testing
- **API Gateway Health**: http://localhost:8000/health
- **Retrieval Health**: http://localhost:8001/health

## 🧪 Test Scenarios

### A. Real-time Query Testing

1. **Open the frontend**: http://localhost:3000
2. **Submit a query** like:
   - "What is machine learning?"
   - "Explain quantum computing"
   - "How does photosynthesis work?"
3. **Expected behavior**:
   - Loading spinner appears
   - Real LLM API call is made (OpenAI/Anthropic)
   - Response shows in chat bubble format
   - Sources are displayed in side panel

### B. Multimodal File Upload Testing

1. **Open multimodal demo**: http://localhost:3000/multimodal-demo
2. **Upload test files**:
   - **PDF document** (tests text extraction)
   - **Image file** (tests metadata extraction)
   - **Text file** (tests content indexing)
3. **Expected behavior**:
   - File uploads successfully
   - Content is extracted and processed
   - File shows as "Processed" and "Indexed"
   - Content becomes searchable in queries

### C. Vector Database Integration Testing

1. **Submit a query** about a topic
2. **Check that**:
   - Web search results are retrieved
   - High-quality results are auto-indexed
   - Subsequent similar queries use indexed content
3. **Upload a file** with content
4. **Query about the uploaded content**:
   - "Summarize the document I uploaded"
   - "What are the key points in my PDF?"

### D. Error Handling Testing

1. **Test network errors**:
   - Disconnect internet, submit query
   - Should show friendly error message
2. **Test file upload errors**:
   - Upload very large file (>100MB)
   - Upload unsupported file type
   - Should show appropriate error messages

## 🔧 Configuration Verification

### Environment Variables
The system should be configured with:
```
USE_VECTOR_DB=true
MOCK_AI_RESPONSES=false
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Service Status
Check that all services show:
- ✅ **Real-time LLM queries enabled**
- ✅ **Vector database active**
- ✅ **Auto-indexing enabled**
- ✅ **Multimodal processing ready**

## 🚨 Troubleshooting

### Services Not Starting
1. **Check Python environment**: `.\venv\Scripts\python.exe --version`
2. **Check dependencies**: Missing packages like `aiofiles`, `python-docx`
3. **Check ports**: Ensure 8000, 8001, 3000 are available

### Frontend Not Connecting
1. **Check API base URL**: Should point to `http://localhost:8000`
2. **Check CORS**: API Gateway should allow frontend origin
3. **Check network tab**: Look for 404/500 errors in browser

### LLM Queries Failing
1. **Check API keys**: OpenAI/Anthropic keys in environment
2. **Check timeout**: Should be 15 seconds for LLM calls
3. **Check mock mode**: Should be disabled (`MOCK_AI_RESPONSES=false`)

### File Upload Issues
1. **Check multimodal service**: Should be running on port 8006
2. **Check file size**: Must be under 100MB
3. **Check file types**: See supported types in multimodal demo

## 📊 Expected Performance

### Response Times
- **Simple queries**: 2-5 seconds
- **Complex queries**: 5-15 seconds  
- **File upload**: 1-30 seconds (depending on size/type)
- **File processing**: 5-60 seconds (depending on content)

### Real-time Features
- ✅ **No mocking**: All LLM calls are real
- ✅ **Auto-indexing**: Web results stored for future use
- ✅ **Content extraction**: Full text from PDFs, transcription from videos
- ✅ **Hybrid search**: Vector + keyword + web search

## 🎯 Success Criteria

### ✅ System is working correctly if:
1. **Frontend loads** without errors
2. **Queries submit** and return real LLM responses
3. **Files upload** and process successfully
4. **Error messages** are user-friendly
5. **Content is indexed** and searchable
6. **Services communicate** properly via APIs

### ❌ Issues to report:
1. Services fail to start
2. Frontend shows blank/error pages
3. Queries hang or return mock responses
4. File uploads fail or don't process
5. Error messages are technical/unhelpful
6. Performance is significantly slower than expected

---

**Ready to test!** Start with `start_services.bat` and open http://localhost:3000
