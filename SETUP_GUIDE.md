# Universal Knowledge Hub - Setup Guide

## 🚀 Quick Start

The Universal Knowledge Hub is an AI-powered research platform that combines web search, AI synthesis, and collaborative knowledge management. This guide will help you get the platform running on your local machine.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** (3.11+ recommended)
- **Node.js 18+** (20+ recommended)
- **npm** (comes with Node.js)
- **Git**

### Optional Dependencies
- **Redis** (for caching and session management)
- **PostgreSQL** (for persistent data storage)
- **Docker** (for containerized deployment)

## 🔧 Installation

### Method 1: Automated Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd universal-knowledge-hub
   ```

2. **Run the automated setup script**
   ```bash
   python scripts/start_development.py
   ```

   This script will:
   - Create a `.env` file from the template
   - Set up Python virtual environment
   - Install Python dependencies
   - Install Node.js dependencies
   - Start both backend and frontend servers

### Method 2: Manual Setup

1. **Set up environment variables**
   ```bash
   cp env.template .env
   ```

2. **Edit `.env` file**
   Update the following required API keys:
   ```env
   OPENAI_API_KEY=your-openai-api-key-here
   ANTHROPIC_API_KEY=your-anthropic-api-key-here
   ```

3. **Install Python dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Start the backend**
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   python -m uvicorn api.main:app --host 0.0.0.0 --port 8002 --reload
   ```

6. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

## 🔑 API Keys Setup

### Required API Keys

1. **OpenAI API Key**
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Create a new API key
   - Add it to your `.env` file: `OPENAI_API_KEY=sk-...`

2. **Anthropic API Key** (Optional but recommended)
   - Visit [Anthropic Console](https://console.anthropic.com/)
   - Create a new API key
   - Add it to your `.env` file: `ANTHROPIC_API_KEY=sk-ant-...`

### Optional API Keys

3. **Pinecone API Key** (for vector search)
   - Visit [Pinecone Console](https://app.pinecone.io/)
   - Create a new API key and index
   - Add to `.env`:
     ```env
     PINECONE_API_KEY=your-pinecone-key
     PINECONE_ENVIRONMENT=us-west1-gcp
     PINECONE_INDEX_NAME=ukp-knowledge-base
     ```

4. **Google Search API Key** (for web search)
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Custom Search API
   - Create credentials
   - Add to `.env`: `GOOGLE_API_KEY=your-google-api-key`

## 🌐 Accessing the Application

Once everything is running, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8002
- **API Documentation**: http://localhost:8002/docs
- **Health Check**: http://localhost:8002/health

## 🧪 Testing the Setup

1. **Test the backend**
   ```bash
   curl http://localhost:8002/health
   ```

2. **Test the frontend**
   - Open http://localhost:3000 in your browser
   - Try submitting a research query

3. **Test API endpoints**
   ```bash
   # Submit a test query
   curl -X POST http://localhost:8002/query \
     -H "Content-Type: application/json" \
     -d '{"query": "What is quantum computing?"}'
   ```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find and kill processes using the ports
   lsof -ti:8002 | xargs kill -9
   lsof -ti:3000 | xargs kill -9
   ```

2. **Node.js dependencies issues**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Python dependencies issues**
   ```bash
   rm -rf .venv
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **API key errors**
   - Ensure your API keys are correctly set in `.env`
   - Check that you have sufficient credits/quota
   - Verify the API keys are valid

5. **Frontend build errors**
   ```bash
   cd frontend
   npm run build
   ```

### Debug Mode

To run with debug logging:

```bash
# Backend with debug
python -m uvicorn api.main:app --host 0.0.0.0 --port 8002 --reload --log-level debug

# Frontend with debug
cd frontend
DEBUG=* npm run dev
```

## 📁 Project Structure

```
universal-knowledge-hub/
├── api/                    # Backend API (FastAPI)
│   ├── main.py            # Main application
│   ├── auth.py            # Authentication
│   ├── models.py          # Data models
│   └── ...
├── frontend/              # Frontend (Next.js)
│   ├── src/
│   │   ├── app/          # Pages
│   │   ├── components/   # React components
│   │   └── lib/          # Utilities
│   └── ...
├── agents/               # AI agents
├── scripts/              # Setup and utility scripts
├── tests/                # Test files
├── requirements.txt       # Python dependencies
├── env.template          # Environment template
└── README.md            # This file
```

## 🚀 Development Workflow

1. **Start development servers**
   ```bash
   python scripts/start_development.py
   ```

2. **Make changes**
   - Backend changes auto-reload
   - Frontend changes auto-reload

3. **Run tests**
   ```bash
   # Backend tests
   pytest tests/

   # Frontend tests
   cd frontend
   npm test
   ```

4. **Code quality checks**
   ```bash
   # Backend linting
   flake8 api/
   black api/

   # Frontend linting
   cd frontend
   npm run lint
   ```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```env
# Server Configuration
UKP_HOST=0.0.0.0
UKP_PORT=8002
UKP_LOG_LEVEL=info

# Security
SECRET_KEY=your-secret-key
API_KEY_SECRET=your-api-key-secret

# AI Configuration
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# Database (optional)
REDIS_URL=redis://localhost:6379/0
```

### Customization

1. **Change AI models**
   - Edit `OPENAI_MODEL` in `.env`
   - Available: `gpt-4`, `gpt-3.5-turbo`, `claude-3-sonnet-20240229`

2. **Adjust response settings**
   - `OPENAI_MAX_TOKENS`: Maximum response length
   - `OPENAI_TEMPERATURE`: Response creativity (0.0-1.0)

3. **Configure caching**
   - Set up Redis for better performance
   - Adjust cache TTL settings

## 📊 Monitoring

### Health Checks

- Backend: `GET /health`
- Frontend: Check browser console
- Database: Check connection status

### Logs

- Backend logs: Console output
- Frontend logs: Browser developer tools
- Error tracking: Check application logs

## 🚀 Deployment

For production deployment, see:
- `PRODUCTION_DEPLOYMENT_GUIDE.md`
- `DEPLOYMENT_GUIDE.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Check API key configuration
4. Ensure all dependencies are installed
5. Try the automated setup script

## 📚 Additional Resources

- [API Documentation](http://localhost:8002/docs)
- [Frontend Documentation](frontend/README.md)
- [Backend Architecture](BACKEND_INDUSTRY_ANALYSIS.md)
- [Security Guide](SECURITY.md)
- [Testing Guide](tests/README.md)

---

**Happy researching! 🚀** 