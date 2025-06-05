# Gemini Fullstack LangGraph Enhanced

A specialized AI agent assistant for automated software project management with 24/7 support and autonomous operation. This enhanced version features multi-LLM provider support, real-time monitoring, and a comprehensive Docker-based infrastructure for production deployment.

![Gemini Fullstack LangGraph](./app.png)

## ✨ Enhanced Features

### 🤖 Multi-LLM Provider Support
- **Primary**: Google Gemini (gemini-2.0-flash) for optimal performance
- **Fallback**: OpenAI GPT (gpt-4o) and Anthropic Claude (claude-3-5-sonnet)
- **Automatic failover** and load balancing between providers
- **Real-time provider status** monitoring and health checks

### 🎨 Enhanced User Interface
- **Real-time agent activity** monitoring (thinking, searching, analyzing)
- **Multi-conversation support** with persistent chat history
- **Performance metrics** dashboard with response times and provider status
- **Project management** interface for task tracking and automation

### 🏗️ Production-Ready Infrastructure
- **Docker Compose** orchestration with PostgreSQL and Redis
- **Health monitoring** and automatic service recovery
- **Persistent data storage** with backup capabilities
- **Load balancing** and SSL termination support

### 🔧 Advanced Agent Capabilities
- **Dynamic search query generation** using multiple LLM providers
- **Integrated web research** via Google Search API
- **Reflective reasoning** to identify knowledge gaps and refine searches
- **Citation generation** with source verification and linking
- **Background task processing** with real-time status updates

## 🏗️ Architecture Overview

### System Components
- **Frontend**: React + TypeScript with enhanced UI components
- **Backend**: LangGraph + FastAPI with multi-LLM support
- **Database**: PostgreSQL for persistent state and conversation history
- **Cache**: Redis for real-time pub/sub and background task queues
- **Infrastructure**: Docker Compose orchestration with health monitoring

### Project Structure
```
├── frontend/          # React application with enhanced UI
├── backend/           # LangGraph agent and FastAPI server
├── docs/             # Documentation and guides
├── docker-compose.yml # Production infrastructure
├── Dockerfile        # Multi-stage build configuration
└── nginx.conf        # Load balancer configuration
```

## 🚀 Quick Start (Recommended)

### Prerequisites
- **Docker** and **Docker Compose** (recommended for full infrastructure)
- **API Keys**:
  - `GEMINI_API_KEY` (required)
  - `LANGSMITH_API_KEY` (required for production)
  - `OPENAI_API_KEY` (optional, for fallback)
  - `ANTHROPIC_API_KEY` (optional, for fallback)

### 1. Environment Setup
Create a `.env` file in the project root:
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here

# Optional (for multi-LLM support)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 2. Build and Deploy
```bash
# Build the enhanced image
docker build -t gemini-fullstack-langgraph-enhanced .

# Start all services
docker-compose up -d
```

### 3. Access the Application
- **Main Application**: http://localhost:8123/app/
- **API Health Check**: http://localhost:8123/api/v1/enhanced/health
- **API Documentation**: http://localhost:8123/docs

## 🛠️ Development Environment

### Local Development (Hot Reloading)
```bash
# Install dependencies
cd backend && pip install -e .
cd ../frontend && npm install

# Start development servers
make dev
```

### Development with Docker (Recommended)
```bash
# Start with development profiles (includes admin interfaces)
docker-compose --profile dev up -d

# Access admin interfaces
# Redis Commander: http://localhost:8081
# pgAdmin: http://localhost:8080 (admin@example.com / admin)
```

## How the Backend Agent Works (High-Level)

The core of the backend is a LangGraph agent defined in `backend/src/agent/graph.py`. It follows these steps:

![Agent Flow](./agent.png)

1.  **Generate Initial Queries:** Based on your input, it generates a set of initial search queries using a Gemini model.
2.  **Web Research:** For each query, it uses the Gemini model with the Google Search API to find relevant web pages.
3.  **Reflection & Knowledge Gap Analysis:** The agent analyzes the search results to determine if the information is sufficient or if there are knowledge gaps. It uses a Gemini model for this reflection process.
4.  **Iterative Refinement:** If gaps are found or the information is insufficient, it generates follow-up queries and repeats the web research and reflection steps (up to a configured maximum number of loops).
5.  **Finalize Answer:** Once the research is deemed sufficient, the agent synthesizes the gathered information into a coherent answer, including citations from the web sources, using a Gemini model.

## 🐳 Production Deployment

### Docker Compose (Recommended)
The enhanced version includes a complete production infrastructure with PostgreSQL, Redis, and optional admin interfaces.

```bash
# Build the enhanced image
docker build -t gemini-fullstack-langgraph-enhanced .

# Start production environment
docker-compose up -d

# Check service health
docker-compose ps
curl http://localhost:8123/api/v1/enhanced/health
```

### Production with Load Balancing
```bash
# Start with production profile (includes Nginx)
docker-compose --profile prod up -d
```

### Environment Variables for Production
```bash
# Core Configuration
GEMINI_API_KEY=your_production_gemini_key
LANGSMITH_API_KEY=your_production_langsmith_key
OPENAI_API_KEY=your_production_openai_key
ANTHROPIC_API_KEY=your_production_anthropic_key

# Enhanced Features
ENABLE_ENHANCED_UI=true
ENABLE_MULTI_LLM=true
ENABLE_AGENT_ROUTING=true

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=10
```

## 📊 Monitoring & Health Checks

### Service Health
- **Application Health**: `http://localhost:8123/api/v1/enhanced/health`
- **Database Status**: Automatic health checks with connection pooling
- **Redis Status**: Pub/sub and cache monitoring
- **LLM Provider Status**: Real-time provider availability

### Admin Interfaces (Development)
- **Redis Commander**: `http://localhost:8081` (Redis management)
- **pgAdmin**: `http://localhost:8080` (PostgreSQL management)
  - Email: `admin@example.com`
  - Password: `admin`

## 🔧 Enhanced Technologies

### Core Stack
- **[React 18](https://reactjs.org/)** with TypeScript and Vite
- **[Tailwind CSS](https://tailwindcss.com/)** for responsive design
- **[Shadcn UI](https://ui.shadcn.com/)** for modern components
- **[LangGraph](https://github.com/langchain-ai/langgraph)** for agent workflows
- **[FastAPI](https://fastapi.tiangolo.com/)** for high-performance APIs

### Infrastructure
- **[PostgreSQL 16](https://www.postgresql.org/)** for persistent data
- **[Redis 6](https://redis.io/)** for caching and pub/sub
- **[Docker Compose](https://docs.docker.com/compose/)** for orchestration
- **[Nginx](https://nginx.org/)** for load balancing (production)

### LLM Providers
- **[Google Gemini](https://ai.google.dev/models/gemini)** (gemini-2.0-flash)
- **[OpenAI GPT](https://openai.com/api/)** (gpt-4o)
- **[Anthropic Claude](https://www.anthropic.com/)** (claude-3-5-sonnet)

## 📚 Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - System design and components
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment instructions
- **[Development Rules](docs/RULES.md)** - Development guidelines and best practices

## 🚨 Troubleshooting

### Common Issues
```bash
# Container won't start
docker-compose logs langgraph-api

# Database connection issues
docker-compose exec langgraph-postgres pg_isready -U postgres

# Check API keys
docker-compose exec langgraph-api env | grep API_KEY
```

### Performance Optimization
- **Database**: Connection pooling and proper indexing
- **Cache**: Redis optimization for pub/sub and background tasks
- **LLM**: Provider routing and fallback strategies

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

---

**🚀 Ready to deploy your AI agent assistant? Follow the [Deployment Guide](docs/DEPLOYMENT.md) for detailed instructions!**