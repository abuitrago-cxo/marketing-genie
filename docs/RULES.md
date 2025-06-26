# Development Rules and Guidelines

## 🔄 Project Awareness & Context

- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASK.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.
- **Follow the original Google Gemini fullstack langgraph quickstart repository patterns** for consistency and maintainability.

## 🏗️ Project Architecture (Based on Original Google Gemini Repository)

### Core Architecture Principles

- **LangGraph-First**: All agent workflows must use LangGraph for state management and execution control
- **FastAPI Backend**: Single FastAPI application serving both API endpoints and frontend static files
- **React Frontend**: Vite-based React application with TypeScript and Tailwind CSS
- **Modular Design**: Clear separation between agent logic, API endpoints, and UI components

### Project Structure (Standard)

```
├── backend/                    # Python backend (LangGraph + FastAPI)
│   ├── src/agent/             # Core agent logic (follows original structure)
│   │   ├── app.py            # Main FastAPI application (entry point)
│   │   ├── graph.py          # Original LangGraph workflow (core)
│   │   ├── state.py          # LangGraph state schemas
│   │   ├── configuration.py  # Agent configuration
│   │   ├── prompts.py        # LLM prompts and templates
│   │   └── utils.py          # Utility functions
│   ├── src/api/              # API endpoint modules
│   │   ├── enhanced_endpoints.py    # Enhanced features API
│   │   ├── specialized_endpoints.py # Multi-agent system API
│   │   └── github_endpoints.py      # GitHub integration API
│   ├── langgraph.json        # LangGraph configuration (required)
│   └── pyproject.toml        # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components (organized by feature)
│   │   ├── App.tsx          # Main React application
│   │   ├── main.tsx         # React entry point
│   │   └── global.css       # Global styles
│   ├── index.html           # HTML template
│   ├── vite.config.ts       # Vite configuration
│   └── package.json         # Node.js dependencies
├── docker-compose.yml        # Infrastructure orchestration
├── Dockerfile               # Multi-stage build
└── .env                     # Environment variables
```

## 🧱 Code Structure & Modularity

### Backend Structure Rules

- **`backend/src/agent/`**: Core agent logic following original Google Gemini patterns
  - `app.py`: Main FastAPI application with frontend mounting
  - `graph.py`: Primary LangGraph workflow (original 5-node flow)
  - `state.py`: LangGraph state schemas and type definitions
  - `configuration.py`: Agent configuration and LLM settings
- **`backend/src/api/`**: API endpoint modules grouped by functionality
- **`backend/langgraph.json`**: Required LangGraph configuration file
- **Never create a file longer than 2000 lines** - split into logical modules
- **Use relative imports within the agent package**: `from .state import OverallState`

### Frontend Structure Rules

- **`frontend/src/components/`**: React components organized by feature/domain
  - `enhanced/`: Enhanced UI components
  - `specialized/`: Multi-agent system components
  - `auth/`: Authentication components
  - `ui/`: Reusable UI components (Shadcn)
- **`frontend/src/App.tsx`**: Main React application component
- **`frontend/src/main.tsx`**: React entry point with routing setup
- **Use TypeScript for all components** with strict type checking
- **Follow React functional component patterns** with hooks

## 🧪 Testing & Reliability

- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.
- **Test LangGraph workflows** using the built-in testing utilities.

## ✅ Task Completion

- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a "Discovered During Work" section.

## 📎 Style & Conventions

- Follow consistent code formatting and validation standards.
- **Python**: Use Black formatting and type hints for all functions.
- **TypeScript**: Use strict TypeScript with no `any` types allowed.

## 📚 Documentation & Explainability

- **Update `README.md`** when new features are added, dependencies change, or setup steps are modified.
- **Comment non-obvious code** and ensure everything is understandable to a mid-level developer.
- When writing complex logic, **add an inline `# Reason:` comment** explaining the why, not just the what.

## 🧠 AI Behavior Rules

- **Never assume missing context. Ask questions if uncertain.**
- **Never hallucinate libraries or functions** – only use known, verified Python packages.
- **Always confirm file paths and module names** exist before referencing them in code or tests.
- **Never delete or overwrite existing code** unless explicitly instructed to or if part of a task from `TASK.md`.

## 🐳 Docker & Infrastructure Rules

### Container Management

- **Use Docker Compose for development and production** - it provides the complete infrastructure stack
- **Always use health checks** in Docker services to ensure proper startup order
- **Environment variables should be documented** in both `.env.example` and docker-compose.yml
- **Never hardcode secrets** - always use environment variables

### Database & Cache

- **PostgreSQL is the primary database** - used for LangGraph state, threads, runs, and application data
- **Redis is used for pub-sub and caching** - enables real-time streaming and background task management
- **Always run database migrations** on startup through the application
- **Use connection pooling** for database connections

### Multi-Service Architecture

- **langgraph-api**: Main application container (frontend + backend)
- **langgraph-postgres**: PostgreSQL database with persistent storage
- **langgraph-redis**: Redis cache and pub-sub broker
- **redis-commander**: Redis admin interface (dev profile only)
- **pgadmin**: PostgreSQL admin interface (dev profile only)
- **nginx**: Load balancer and reverse proxy (prod profile only)

## 🤖 LLM Provider Rules

### Multi-Provider Support

- **Support multiple LLM providers**: Google Gemini, OpenAI GPT, Anthropic Claude
- **Always have fallback providers** configured in case primary provider fails
- **Use environment variables** for API keys: `GEMINI_API_KEY`
- **Implement graceful degradation** when providers are unavailable

### Provider Configuration

- **Primary provider**: Google Gemini (gemini-2.0-flash)
- **Fallback providers**: OpenAI GPT (gpt-4o), Anthropic Claude (claude-3-5-sonnet)
- **Provider routing**: Automatic failover based on availability and performance
- **Rate limiting**: Implement per-provider rate limiting to avoid API quota issues

## 🎨 Frontend Rules

### React & TypeScript

- **Use TypeScript for all new components** - provides better type safety and developer experience
- **Follow React best practices** - functional components, hooks, proper state management
- **Use Tailwind CSS** for styling - consistent design system
- **Implement Shadcn UI components** for common UI elements

### Enhanced UI Features

- **Real-time updates**: Use WebSocket connections for live agent status
- **Activity monitoring**: Show agent thinking, searching, analyzing states
- **Multi-conversation support**: Allow multiple concurrent conversations
- **Performance metrics**: Display response times and provider status

## 🔧 Backend Rules (Based on Original Google Gemini Repository)

### LangGraph Architecture (Core Pattern)

- **Follow the original 5-node workflow**: route_task → generate_query → web_research → reflection → finalize_answer
- **Use StateGraph with OverallState**: All workflows must extend the original state schema
- **Implement proper node functions**: Each node must accept (state, config) and return state updates
- **Use conditional edges**: Implement proper flow control with conditional edges
- **Maintain langgraph.json**: Required configuration file for LangGraph deployment

### Original Repository Structure Compliance

- **Main entry point**: `backend/src/agent/app.py` (FastAPI application)
- **Core workflow**: `backend/src/agent/graph.py` (original LangGraph implementation)
- **State management**: `backend/src/agent/state.py` (OverallState schema)
- **Configuration**: `backend/src/agent/configuration.py` (LLM and agent settings)
- **Frontend mounting**: App serves frontend at `/app` route, APIs at `/api`

### LangGraph Node Implementation Rules

- **Node function signature**: `def node_name(state: OverallState, config: RunnableConfig) -> Dict[str, Any]`
- **State updates**: Return dictionary with state field updates, never modify state directly
- **Error handling**: Use try-catch blocks and return error states when needed
- **Tracing**: Use `@traceable` decorator for LangSmith integration
- **Streaming**: Implement streaming for long-running operations

### API Design (Following Original Patterns)

- **FastAPI application**: Single app instance in `app.py` with router inclusion
- **Router organization**: Separate routers by feature (specialized, enhanced, github, mcp)
- **Endpoint prefixes**: `/api/v1/{feature}/` for all API endpoints
- **Health checks**: Implement `/health` and `/api/health` endpoints
- **Frontend serving**: Mount frontend build at `/app` route

### State Management (LangGraph Patterns)

- **Extend OverallState**: All new state schemas should extend the original
- **Immutable updates**: Always return new state, never mutate existing state
- **Type safety**: Use TypedDict and proper type annotations
- **Persistence**: LangGraph automatically handles state persistence in PostgreSQL
- **Thread management**: Use LangGraph's built-in thread and run management

### Security & Performance

- **Input validation**: Validate all user inputs and API parameters
- **Rate limiting**: Implement API rate limiting to prevent abuse
- **Logging**: Comprehensive logging for debugging and monitoring
- **Monitoring**: Health checks, metrics, and performance monitoring

## 🎯 Original Repository Patterns (Google Gemini Compliance)

### Core Workflow Pattern (Must Follow)

```python
# Original 5-node workflow from graph.py
route_task → generate_query → web_research → reflection → finalize_answer

# Node implementation pattern:
def node_name(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    """Node function following original patterns"""
    try:
        # Node logic here
        return {"field_name": updated_value}
    except Exception as e:
        return {"error": str(e)}
```

### State Schema Pattern (Extend, Don't Replace)

```python
# Always extend OverallState from state.py
from .state import OverallState

class EnhancedState(OverallState):
    """Extended state for new features"""
    new_field: Optional[str] = None

# Never modify OverallState directly - extend it
```

### Configuration Pattern (Follow configuration.py)

```python
# Use Configuration class for all LLM settings
from .configuration import Configuration

# Access configuration in nodes:
def my_node(state: OverallState, config: RunnableConfig) -> Dict[str, Any]:
    configuration = Configuration.from_runnable_config(config)
    llm = configuration.llm
    # Use llm for operations
```

### Frontend Integration Pattern (Follow app.py)

```python
# Mount frontend at /app route (never change this)
app.mount("/app", create_frontend_router(), name="frontend")

# API routes use /api prefix
app.include_router(router, prefix="/api/v1/feature")

# Health checks at /health and /api/health
```

### LangGraph Deployment Pattern (langgraph.json)

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agent/graph.py:graph"
  },
  "http": {
    "app": "./src/agent/app.py:app"
  },
  "env": ".env"
}
```

### Development Commands (Follow Original)

```bash
# Development (original pattern)
make dev

# Production build (original pattern)
docker build -t gemini-fullstack-langgraph-enhanced .

# Never change these core commands - they're part of the original architecture
```

## 🚀 Deployment Rules

### Development Environment

- **Use `make dev`** for local development - starts both frontend and backend
- **Hot reloading**: Both frontend and backend support hot reloading
- **Environment files**: Use `.env` files for local configuration
- **Development profiles**: Use docker-compose profiles for optional services

### Production Environment

- **Use Docker Compose** for production deployment
- **Environment variables**: All configuration through environment variables
- **Health checks**: Comprehensive health monitoring for all services
- **Persistent storage**: PostgreSQL data persistence with Docker volumes
- **Load balancing**: Nginx for production load balancing and SSL termination

### Monitoring & Maintenance

- **LangSmith integration**: For agent performance monitoring and debugging
- **Log aggregation**: Centralized logging for all services
- **Backup strategies**: Regular database backups for production
- **Update procedures**: Rolling updates with zero downtime

## 📋 Troubleshooting Rules

### Common Issues

- **Container startup failures**: Check health checks and dependency order
- **Database connection issues**: Verify PostgreSQL container health and connection strings
- **LLM provider failures**: Check API keys and implement fallback providers
- **Frontend build issues**: Verify Node.js version and dependency installation

### Debugging Procedures

- **Use Docker logs**: `docker logs <container_name>` for service debugging
- **Health check endpoints**: Use `/api/v1/enhanced/health` for system status
- **Database inspection**: Use pgAdmin for database debugging
- **Redis monitoring**: Use redis-commander for cache inspection

### Performance Optimization

- **Database indexing**: Proper indexes for LangGraph state queries
- **Connection pooling**: Optimize database connection pool settings
- **Caching strategies**: Use Redis for frequently accessed data
- **Resource limits**: Set appropriate CPU and memory limits for containers

---

## 📚 **CONSOLIDATED WORKFLOW DOCUMENTATION ARCHIVE**

*This section contains consolidated workflow and deployment information from multiple documentation files that were merged into this rules document for unified documentation management.*

### 🐳 **Docker Workflow Documentation**

*(Consolidated from DOCKER_UPDATE_REPORT.md)*

#### **Enhanced Docker Configuration - Production Ready**

**Updated Infrastructure Components:**

- ✅ **Enhanced API Service**: `gemini-fullstack-langgraph-enhanced` with multi-LLM support
- ✅ **PostgreSQL 16**: Persistent database with health checks and connection pooling
- ✅ **Redis 6**: Cache and pub-sub with AOF persistence and memory optimization
- ✅ **Development Tools**: Redis Commander and pgAdmin for development
- ✅ **Production Tools**: Nginx load balancer with SSL termination

**Docker Compose Profiles:**

**Development Profile (`--profile dev`):**

```bash
# Start development environment with admin tools
docker-compose --profile dev up -d

# Includes:
# - Main application (port 8123)
# - PostgreSQL database (port 5433)
# - Redis cache (port 6379)
# - Redis Commander (port 8081) - Redis management
# - pgAdmin (port 8080) - PostgreSQL management
```

**Production Profile (`--profile prod`):**

```bash
# Start production environment with load balancer
docker-compose --profile prod up -d

# Includes:
# - Main application (internal)
# - PostgreSQL database (internal)
# - Redis cache (internal)
# - Nginx load balancer (ports 80/443)
# - SSL termination and rate limiting
```

#### **Enhanced Dockerfile Features**

**Additional System Tools:**

- ✅ **Network Tools**: curl, wget, netcat for connectivity testing
- ✅ **Database Tools**: postgresql-client for database operations
- ✅ **Cache Tools**: redis-tools for Redis operations
- ✅ **Monitoring Tools**: Built-in health check scripts

**Enhanced Dependencies:**

- ✅ **Multi-LLM Support**: langchain-anthropic, langchain-openai
- ✅ **Enhanced FastAPI**: fastapi[all] with complete feature set
- ✅ **Production Features**: uvicorn[standard] with performance optimizations

**Environment Configuration:**

```bash
# Core LLM Providers
GEMINI_API_KEY=your_gemini_api_key

# LangSmith Integration (Optional)
LANGSMITH_API_KEY=your_langsmith_api_key
```

#### **Automation Scripts (Windows)**

**Master Management Console (`manage.bat`):**

- ✅ **Interactive Menu**: Choose from rebuild, restart, logs, cleanup options
- ✅ **Health Monitoring**: Automatic service health verification
- ✅ **Intelligent Rebuild**: Detects changes and rebuilds only when necessary
- ✅ **Log Management**: Advanced log viewing with search and filtering

**Quick Operations:**

- ✅ **`rebuild-and-start.bat`**: Complete rebuild with updated code
- ✅ **`quick-restart.bat`**: Fast restart without rebuild
- ✅ **`dev-start.bat`**: Development mode with admin tools
- ✅ **`stop-all.bat`**: Safe shutdown with cleanup options
- ✅ **`logs-viewer.bat`**: Advanced log visualization

#### **Health Monitoring & Diagnostics**

**Service Health Checks:**

```bash
# Application health
curl http://localhost:8123/api/v1/enhanced/health

# Database connectivity
docker-compose exec langgraph-postgres pg_isready -U postgres

# Redis connectivity
docker-compose exec langgraph-redis redis-cli ping

# Container status
docker-compose ps
```

**Performance Monitoring:**

- ✅ **Resource Usage**: CPU, memory, disk usage per container
- ✅ **Connection Pools**: Database and Redis connection monitoring
- ✅ **Response Times**: API endpoint performance metrics
- ✅ **Error Rates**: Service error tracking and alerting

### 🚀 **Deployment Procedures**

*(Consolidated from docs/DEPLOYMENT.md)*

#### **Production Deployment Checklist**

**Pre-Deployment:**

- [ ] **Environment Variables**: All required API keys configured
- [ ] **SSL Certificates**: Valid certificates for HTTPS (production)
- [ ] **Database Backup**: Current backup of production data
- [ ] **Resource Planning**: Adequate CPU, memory, storage allocated
- [ ] **Network Configuration**: Firewall rules and port access configured

**Deployment Steps:**

1. **Build Enhanced Image**:

   ```bash
   docker build -t gemini-fullstack-langgraph-enhanced .
   ```

2. **Start Production Services**:

   ```bash
   docker-compose --profile prod up -d
   ```

3. **Verify Health**:

   ```bash
   # Check all services
   docker-compose ps

   # Test application
   curl http://localhost:8123/api/v1/enhanced/health
   ```

4. **Monitor Startup**:

   ```bash
   # Watch logs during startup
   docker-compose logs -f
   ```

**Post-Deployment:**

- [ ] **Health Verification**: All services healthy and responding
- [ ] **Database Migration**: Schema updates applied successfully
- [ ] **Performance Testing**: Response times within acceptable limits
- [ ] **Security Scan**: No security vulnerabilities detected
- [ ] **Backup Verification**: Backup systems operational

#### **Rollback Procedures**

**Emergency Rollback:**

```bash
# Stop current deployment
docker-compose down

# Restore previous image
docker tag gemini-fullstack-langgraph-enhanced:previous gemini-fullstack-langgraph-enhanced:latest

# Restart with previous version
docker-compose up -d

# Verify rollback success
curl http://localhost:8123/api/v1/enhanced/health
```

**Database Rollback:**

```bash
# Restore database from backup
docker-compose exec langgraph-postgres pg_restore -U postgres -d langgraph /backup/langgraph_backup.sql

# Verify data integrity
docker-compose exec langgraph-postgres psql -U postgres -d langgraph -c "SELECT COUNT(*) FROM assistant;"
```

### 🔧 **Development Guidelines**

*(Consolidated from development best practices)*

#### **Local Development Setup**

**Prerequisites:**

- Docker Desktop 4.0+ with Docker Compose V2
- Node.js 18+ for frontend development
- Python 3.11+ for backend development
- Git for version control

**Development Workflow:**

1. **Clone Repository**:

   ```bash
   git clone <repository-url>
   cd gemini-fullstack-langgraph-quickstart
   ```

2. **Environment Setup**:

   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit with your API keys
   nano .env
   ```

3. **Start Development Environment**:

   ```bash
   # Option 1: Docker development
   docker-compose --profile dev up -d

   # Option 2: Local development
   make dev
   ```

4. **Access Development Tools**:
   - **Application**: <http://localhost:8123/app/>
   - **API Docs**: <http://localhost:8123/docs>
   - **Redis Commander**: <http://localhost:8081>
   - **pgAdmin**: <http://localhost:8080>

#### **Code Quality Standards**

**Python Backend:**

- ✅ **Type Hints**: All functions must have type annotations
- ✅ **Docstrings**: All public functions must have docstrings
- ✅ **Error Handling**: Comprehensive exception handling
- ✅ **Testing**: Unit tests for all business logic
- ✅ **Linting**: Black formatting and flake8 compliance

**TypeScript Frontend:**

- ✅ **Strict TypeScript**: No `any` types allowed
- ✅ **Component Structure**: Functional components with hooks
- ✅ **State Management**: Proper state management patterns
- ✅ **Testing**: Component tests with React Testing Library
- ✅ **Accessibility**: WCAG 2.1 AA compliance

#### **Git Workflow**

**Branch Strategy:**

- ✅ **main**: Production-ready code
- ✅ **develop**: Integration branch for features
- ✅ **feature/***: Individual feature development
- ✅ **hotfix/***: Critical production fixes

**Commit Standards:**

```bash
# Commit message format
type(scope): description

# Examples
feat(agents): add real specialized agent classes
fix(ui): resolve scroll issues in chat interface
docs(readme): update deployment instructions
```

**Pull Request Process:**

1. **Feature Branch**: Create from develop
2. **Implementation**: Follow coding standards
3. **Testing**: All tests pass
4. **Review**: Code review required
5. **Merge**: Squash and merge to develop

### 📊 **Monitoring & Maintenance**

*(Consolidated from operational procedures)*

#### **System Monitoring**

**Application Metrics:**

- ✅ **Response Times**: API endpoint performance
- ✅ **Error Rates**: Application error tracking
- ✅ **Agent Performance**: Multi-agent workflow metrics
- ✅ **Resource Usage**: CPU, memory, disk utilization

**Infrastructure Metrics:**

- ✅ **Database Performance**: Query times, connection pool usage
- ✅ **Cache Performance**: Redis hit rates, memory usage
- ✅ **Network Performance**: Request/response times
- ✅ **Container Health**: Service availability and restart counts

#### **Maintenance Procedures**

**Daily Maintenance:**

- [ ] **Health Check**: Verify all services healthy
- [ ] **Log Review**: Check for errors or warnings
- [ ] **Performance Review**: Monitor response times
- [ ] **Backup Verification**: Ensure backups completed successfully

**Weekly Maintenance:**

- [ ] **Security Updates**: Apply security patches
- [ ] **Performance Analysis**: Review performance trends
- [ ] **Capacity Planning**: Monitor resource usage trends
- [ ] **Backup Testing**: Verify backup restoration procedures

**Monthly Maintenance:**

- [ ] **Full System Backup**: Complete system backup
- [ ] **Security Audit**: Comprehensive security review
- [ ] **Performance Optimization**: Optimize based on usage patterns
- [ ] **Documentation Update**: Update operational documentation

#### **Troubleshooting Procedures**

**Common Issues & Solutions:**

**Service Won't Start:**

```bash
# Check container logs
docker-compose logs <service-name>

# Verify environment variables
docker-compose exec <service-name> env | grep API_KEY

# Check resource availability
docker system df
docker system prune -f
```

**Database Connection Issues:**

```bash
# Test database connectivity
docker-compose exec langgraph-postgres pg_isready -U postgres

# Check connection pool
docker-compose exec langgraph-api python -c "from backend.src.database import test_connection; test_connection()"

# Reset database connections
docker-compose restart langgraph-postgres
```

**Performance Issues:**

```bash
# Monitor resource usage
docker stats

# Check database performance
docker-compose exec langgraph-postgres psql -U postgres -d langgraph -c "SELECT * FROM pg_stat_activity;"

# Optimize Redis memory
docker-compose exec langgraph-redis redis-cli info memory
```
