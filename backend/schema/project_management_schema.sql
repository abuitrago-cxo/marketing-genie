-- Project Management Schema for GitHub Import Feature
-- To be executed against PostgreSQL database

-- Projects Table: Stores main project information
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    github_repo_url VARCHAR(2048), -- URL del repositorio GitHub
    github_repo_id VARCHAR(255),   -- ID único del repositorio en GitHub
    github_metadata JSONB,         -- Metadatos adicionales del repositorio (estrellas, forks, etc.)
    repository_analysis TEXT,      -- Análisis generado por LLM
    status VARCHAR(50) DEFAULT 'active',
    priority VARCHAR(50) DEFAULT 'medium',
    team VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255)           -- Usuario que creó/posee el proyecto
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_projects_github_repo_id ON projects(github_repo_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Project Tasks Table: Stores tasks related to projects
CREATE TABLE IF NOT EXISTS project_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(50) DEFAULT 'medium',
    assigned_to VARCHAR(255),
    due_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    github_issue_id VARCHAR(255),  -- ID de issue en GitHub si está vinculado
    github_issue_url VARCHAR(2048), -- URL al issue en GitHub si está vinculado
    ai_generated BOOLEAN DEFAULT FALSE, -- Indica si la tarea fue generada por IA
    metadata JSONB                 -- Metadatos adicionales
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_project_tasks_project_id ON project_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_project_tasks_status ON project_tasks(status);
CREATE INDEX IF NOT EXISTS idx_project_tasks_assigned_to ON project_tasks(assigned_to);

-- Project Milestones Table: Stores milestones for project planning
CREATE TABLE IF NOT EXISTS project_milestones (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    target_date TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ai_generated BOOLEAN DEFAULT FALSE, -- Indica si el milestone fue generado por IA
    metadata JSONB                 -- Metadatos adicionales
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_project_milestones_project_id ON project_milestones(project_id);
CREATE INDEX IF NOT EXISTS idx_project_milestones_status ON project_milestones(status);

-- Agent Long-Term Memory Table: Stores persistent memories for AI agents
CREATE TABLE IF NOT EXISTS agent_long_term_memory (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) NOT NULL,               -- Identificador del agente o tipo de agente
    user_id VARCHAR(255),                         -- ID del usuario asociado (si aplica)
    session_id VARCHAR(255),                      -- ID de la sesión o conversación (thread_id de LangGraph)
    project_id INTEGER REFERENCES projects(id) ON DELETE SET NULL, -- ID del proyecto asociado (si aplica)
    memory_type VARCHAR(100) NOT NULL,            -- Tipo de memoria (ej: 'user_preference', 'project_fact', etc.)
    content TEXT NOT NULL,                        -- Contenido textual de la memoria
    content_vector VECTOR(1536),                  -- Embedding vectorial del contenido (requiere pgvector)
    importance_score REAL DEFAULT 0.5,            -- Puntuación de importancia (0.0 a 1.0)
    last_accessed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, -- Última vez que se accedió a la memoria
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP, -- Cuándo se creó la memoria
    metadata JSONB                                -- Metadatos adicionales
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_agent_ltm_agent_id ON agent_long_term_memory(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_ltm_user_id ON agent_long_term_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_ltm_project_id ON agent_long_term_memory(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_ltm_memory_type ON agent_long_term_memory(memory_type);

-- Uncomment to create vector similarity search index if pgvector is available
-- CREATE INDEX IF NOT EXISTS idx_agent_ltm_content_vector ON agent_long_term_memory USING ivfflat 
--   (content_vector vector_l2_ops) WITH (lists = 100);

-- Function to update 'updated_at' field automatically
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to tables
CREATE TRIGGER update_projects_timestamp BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE PROCEDURE update_timestamp_column();

CREATE TRIGGER update_project_tasks_timestamp BEFORE UPDATE ON project_tasks
FOR EACH ROW EXECUTE PROCEDURE update_timestamp_column();

CREATE TRIGGER update_project_milestones_timestamp BEFORE UPDATE ON project_milestones
FOR EACH ROW EXECUTE PROCEDURE update_timestamp_column();

-- Comment: This schema adds support for project management with GitHub integration
-- and agent long-term memory with vector embeddings (requires pgvector extension)
