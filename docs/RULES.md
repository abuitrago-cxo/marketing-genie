# Development Rules and Guidelines

## 🔄 Project Awareness & Context
- **Always read `PLANNING.md`** at the start of a new conversation to understand the project's architecture, goals, style, and constraints.
- **Check `TASK.md`** before starting a new task. If the task isn't listed, add it with a brief description and today's date.
- **Use consistent naming conventions, file structure, and architecture patterns** as described in `PLANNING.md`.

## 🧱 Code Structure & Modularity
- **Never create a file longer than 2000 lines of code.** If a file approaches this limit, refactor by splitting it into modules or helper files.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Use clear, consistent imports** (prefer relative imports within packages).
- **Never use space between the code lines.**

## 🧪 Testing & Reliability
- **Always create Pytest unit tests for new features** (functions, classes, routes, etc).
- **After updating any logic**, check whether existing unit tests need to be updated. If so, do it.
- **Tests should live in a `/tests` folder** mirroring the main app structure.

## ✅ Task Completion
- **Mark completed tasks in `TASK.md`** immediately after finishing them.
- Add new sub-tasks or TODOs discovered during development to `TASK.md` under a "Discovered During Work" section.

## 📎 Style & Conventions
- Follow consistent code formatting and validation standards.

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
- **Use environment variables** for API keys: `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
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

## 🔧 Backend Rules

### LangGraph Architecture
- **Use LangGraph for agent workflows** - provides state management and execution control
- **Implement proper state management** - persist conversation state in PostgreSQL
- **Use background task queues** - for long-running agent operations
- **Implement streaming responses** - for real-time user feedback

### API Design
- **RESTful API design** - consistent endpoint naming and HTTP methods
- **Enhanced endpoints**: Prefix with `/api/v1/enhanced/` for new features
- **Health checks**: Implement comprehensive health monitoring
- **Error handling**: Proper HTTP status codes and error messages

### Security & Performance
- **Input validation**: Validate all user inputs and API parameters
- **Rate limiting**: Implement API rate limiting to prevent abuse
- **Logging**: Comprehensive logging for debugging and monitoring
- **Monitoring**: Health checks, metrics, and performance monitoring

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
