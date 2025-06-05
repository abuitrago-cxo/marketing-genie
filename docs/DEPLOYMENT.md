# Deployment Guide

## Overview

This guide covers deployment options for the Gemini Fullstack LangGraph Enhanced application, from local development to production environments.

## Prerequisites

### Required Software
- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** for cloning the repository

### Required API Keys
- **GEMINI_API_KEY**: Google Gemini API key (required)
- **LANGSMITH_API_KEY**: LangSmith API key (required for production)
- **OPENAI_API_KEY**: OpenAI API key (optional, for fallback)
- **ANTHROPIC_API_KEY**: Anthropic API key (optional, for fallback)

## Quick Start (Docker Compose)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd gemini-fullstack-langgraph-quickstart
```

### 2. Environment Configuration
Create a `.env` file in the project root:
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
LANGSMITH_API_KEY=your_langsmith_api_key_here

# Optional (for multi-LLM support)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Build and Deploy
```bash
# Build the enhanced image
docker build -t gemini-fullstack-langgraph-enhanced .

# Start all services
docker-compose up -d
```

### 4. Access the Application
- **Main Application**: http://localhost:8123/app/
- **API Health Check**: http://localhost:8123/api/v1/enhanced/health
- **API Documentation**: http://localhost:8123/docs

## Development Environment

### Local Development with Hot Reloading
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

### Development Commands
```bash
# View logs
docker-compose logs -f langgraph-api

# Restart specific service
docker-compose restart langgraph-api

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Production Environment

### Production Deployment
```bash
# Build production image
docker build -t gemini-fullstack-langgraph-enhanced .

# Start with production profile (includes Nginx)
docker-compose --profile prod up -d
```

### Production Configuration

#### Environment Variables
```bash
# Core Configuration
GEMINI_API_KEY=your_production_gemini_key
LANGSMITH_API_KEY=your_production_langsmith_key
OPENAI_API_KEY=your_production_openai_key
ANTHROPIC_API_KEY=your_production_anthropic_key

# Database Configuration
POSTGRES_URI=postgres://postgres:secure_password@langgraph-postgres:5432/postgres?sslmode=disable
REDIS_URI=redis://langgraph-redis:6379

# Enhanced Features
ENABLE_ENHANCED_UI=true
ENABLE_MULTI_LLM=true
ENABLE_AGENT_ROUTING=true

# System Configuration
LOG_LEVEL=INFO
MAX_CONCURRENT_TASKS=10
HEALTH_CHECK_INTERVAL=30
```

#### SSL Configuration (with Nginx)
1. Place SSL certificates in `./ssl/` directory:
   - `cert.pem` (certificate)
   - `key.pem` (private key)

2. Update `nginx.conf` for your domain

3. Start with production profile:
```bash
docker-compose --profile prod up -d
```

### Production Monitoring

#### Health Checks
```bash
# Check all service health
docker-compose ps

# Check application health
curl http://localhost:8123/api/v1/enhanced/health

# Check individual service logs
docker-compose logs langgraph-api
docker-compose logs langgraph-postgres
docker-compose logs langgraph-redis
```

#### Performance Monitoring
- **LangSmith Dashboard**: Monitor agent performance and costs
- **Application Logs**: Structured logging for debugging
- **Database Metrics**: Connection pool and query performance
- **Redis Metrics**: Cache hit rates and pub/sub performance

## Cloud Deployment

### AWS Deployment
```bash
# Using AWS ECS with Docker Compose
docker context create ecs myecscontext
docker context use myecscontext
docker compose up
```

### Google Cloud Deployment
```bash
# Using Google Cloud Run
gcloud run deploy gemini-langgraph \
  --image gcr.io/PROJECT_ID/gemini-fullstack-langgraph-enhanced \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment
```bash
# Using Azure Container Instances
az container create \
  --resource-group myResourceGroup \
  --name gemini-langgraph \
  --image gemini-fullstack-langgraph-enhanced \
  --ports 8000
```

## Scaling Considerations

### Horizontal Scaling
```yaml
# docker-compose.override.yml for scaling
services:
  langgraph-api:
    deploy:
      replicas: 3
    environment:
      - WORKER_PROCESSES=2
```

### Load Balancing
- Use Nginx for HTTP load balancing
- Configure Redis for session sharing
- Implement database connection pooling

### Resource Limits
```yaml
services:
  langgraph-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

## Backup and Recovery

### Database Backup
```bash
# Create backup
docker exec langgraph-postgres pg_dump -U postgres postgres > backup.sql

# Restore backup
docker exec -i langgraph-postgres psql -U postgres postgres < backup.sql
```

### Volume Backup
```bash
# Backup persistent data
docker run --rm -v gemini-fullstack-langgraph-quickstart_langgraph-data:/data \
  -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data
```

## Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
docker-compose logs langgraph-api

# Check health status
docker-compose ps

# Restart with clean state
docker-compose down -v && docker-compose up -d
```

#### Database Connection Issues
```bash
# Check PostgreSQL health
docker-compose exec langgraph-postgres pg_isready -U postgres

# Check connection string
docker-compose exec langgraph-api env | grep POSTGRES_URI
```

#### LLM Provider Issues
```bash
# Check API keys
docker-compose exec langgraph-api env | grep API_KEY

# Check provider status
curl http://localhost:8123/api/v1/enhanced/llm/status
```

### Performance Issues

#### High Memory Usage
- Increase container memory limits
- Optimize database connection pool size
- Implement Redis memory policies

#### Slow Response Times
- Check LLM provider latency
- Optimize database queries
- Implement caching strategies

### Security Considerations

#### API Key Management
- Use Docker secrets for production
- Rotate API keys regularly
- Monitor API usage and costs

#### Network Security
- Use internal Docker networks
- Implement rate limiting
- Configure firewall rules

## Maintenance

### Regular Tasks
- Monitor disk usage for PostgreSQL volumes
- Review and rotate logs
- Update Docker images for security patches
- Monitor API usage and costs

### Updates
```bash
# Update to latest version
git pull origin main
docker build -t gemini-fullstack-langgraph-enhanced .
docker-compose up -d --force-recreate
```

### Monitoring Setup
- Set up log aggregation (ELK stack, Fluentd)
- Configure alerting for service failures
- Monitor resource usage and performance metrics
