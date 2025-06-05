# System Architecture

## Overview

This project implements a specialized AI agent assistant for automated software project management with 24/7 support and autonomous operation. The system is built on a modern, scalable architecture using Docker containers, multiple LLM providers, and real-time communication.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (LangGraph)   │◄──►│   (PostgreSQL)  │
│   Port: 8123    │    │   Port: 8000    │    │   Port: 5433    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │     Redis       │              │
         └──────────────►│   (Cache/PubSub)│◄─────────────┘
                        │   Port: 6379    │
                        └─────────────────┘
```

## Component Details

### 1. Frontend (React + TypeScript)
- **Technology**: React 18 with TypeScript, Vite build system
- **UI Framework**: Tailwind CSS + Shadcn UI components
- **Features**:
  - Real-time agent status monitoring
  - Multi-conversation support
  - Enhanced chat interface with activity tracking
  - Project management dashboard
  - Performance metrics visualization

### 2. Backend (LangGraph + FastAPI)
- **Core Framework**: LangGraph for agent workflows, FastAPI for API endpoints
- **LLM Providers**: 
  - Primary: Google Gemini (gemini-2.0-flash)
  - Fallback: OpenAI GPT (gpt-4o), Anthropic Claude (claude-3-5-sonnet)
- **Features**:
  - Multi-provider LLM routing with automatic failover
  - Background task processing with Redis queues
  - Real-time streaming responses
  - Comprehensive health monitoring
  - Enhanced API endpoints for system management

### 3. Database Layer (PostgreSQL)
- **Purpose**: 
  - LangGraph state persistence (threads, runs, checkpoints)
  - User conversation history
  - Agent configuration and routing rules
  - Performance metrics and analytics
- **Features**:
  - Connection pooling for high performance
  - Automatic migrations on startup
  - Persistent storage with Docker volumes

### 4. Cache & Pub/Sub (Redis)
- **Purpose**:
  - Real-time message streaming between frontend and backend
  - Background task queue management
  - Session and temporary data caching
  - Agent status broadcasting
- **Features**:
  - Pub/Sub for real-time updates
  - Task queue with "exactly once" semantics
  - Connection pooling and health monitoring

## Agent Workflow Architecture

```
┌─────────────────┐
│  User Input     │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Query Analysis  │
│ & Routing       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Research Agent  │    │ Analysis Agent  │    │ Synthesis Agent │
│ (Web Search)    │◄──►│ (Reflection)    │◄──►│ (Final Answer)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Knowledge Base  │    │ Gap Analysis    │    │ Citation        │
│ Building        │    │ & Iteration     │    │ Generation      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Multi-LLM Provider Architecture

```
┌─────────────────┐
│   LLM Manager   │
└─────────┬───────┘
          │
    ┌─────┴─────┐
    │  Router   │
    └─────┬─────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Gemini  │ │ OpenAI  │ │ Claude  │
│ Primary │ │Fallback │ │Fallback │
└─────────┘ └─────────┘ └─────────┘
```

### Provider Selection Logic
1. **Health Check**: Verify provider availability
2. **Load Balancing**: Distribute requests based on current load
3. **Fallback Chain**: Automatic failover on errors
4. **Rate Limiting**: Respect API quotas and limits

## Docker Container Architecture

### Core Services
- **langgraph-api**: Main application container
  - Combines frontend build and backend API
  - Health checks on `/api/v1/enhanced/health`
  - Auto-restart on failure

- **langgraph-postgres**: Database service
  - PostgreSQL 16 with persistent storage
  - Health checks with `pg_isready`
  - Automatic backup capabilities

- **langgraph-redis**: Cache and message broker
  - Redis 6 for pub/sub and caching
  - Health checks with `redis-cli ping`
  - Memory optimization for production

### Development Services (Optional)
- **redis-commander**: Redis admin interface (port 8081)
- **pgadmin**: PostgreSQL admin interface (port 8080)

### Production Services (Optional)
- **nginx**: Load balancer and reverse proxy
  - SSL termination
  - Static file serving
  - Rate limiting and security headers

## Data Flow

### 1. User Interaction Flow
```
User Input → Frontend → WebSocket → Backend → LLM Provider → Response → Frontend → User
```

### 2. Agent Processing Flow
```
Query → Router → Agent Graph → State Updates → Database → Real-time Updates → Frontend
```

### 3. Background Task Flow
```
Task Creation → Redis Queue → Worker Process → State Updates → Pub/Sub → Frontend Notification
```

## Security Architecture

### Authentication & Authorization
- Environment-based API key management
- No hardcoded secrets in containers
- Secure communication between services

### Network Security
- Internal Docker network for service communication
- Exposed ports only for necessary services
- Optional SSL termination with Nginx

### Data Protection
- Encrypted database connections
- Secure Redis communication
- Input validation and sanitization

## Scalability Considerations

### Horizontal Scaling
- Stateless backend design allows multiple instances
- Redis pub/sub enables multi-instance communication
- Database connection pooling handles concurrent requests

### Performance Optimization
- Frontend build optimization with Vite
- Database indexing for LangGraph queries
- Redis caching for frequently accessed data
- Connection pooling for all external services

### Monitoring & Observability
- Comprehensive health checks for all services
- LangSmith integration for agent performance monitoring
- Structured logging for debugging and analytics
- Performance metrics collection and visualization

## Development vs Production

### Development Environment
- Hot reloading for both frontend and backend
- Development profiles for admin interfaces
- Local environment variable configuration
- Debug logging and detailed error messages

### Production Environment
- Optimized frontend builds
- Production logging levels
- Health monitoring and auto-restart
- Persistent data storage with backups
- Load balancing and SSL termination

## Future Architecture Considerations

### Planned Enhancements
- Microservices decomposition for larger scale
- Kubernetes deployment for cloud environments
- Advanced monitoring with Prometheus/Grafana
- Multi-tenant support with isolated data
- Advanced caching strategies with CDN integration
