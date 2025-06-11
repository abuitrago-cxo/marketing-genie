# Integración con LangSmith para Trazabilidad de Grafos LangGraph

## Introducción

Este documento detalla los patrones de integración con LangSmith para asegurar trazabilidad completa en todos los grafos LangGraph del sistema, con énfasis en la funcionalidad de importación de proyectos GitHub. La implementación sigue el modelo utilizado en el repositorio original `google-gemini/gemini-fullstack-langgraph-quickstart`.

## Configuración Básica

### Variables de Entorno

El sistema ya cuenta con las siguientes variables configuradas en `.env`:

```
LANGSMITH_API_KEY=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
LANGSMITH_PROJECT=ai-agent-3-specialization
```

Esto permite que LangChain/LangGraph envíe automáticamente trazas a LangSmith. Para asegurar consistencia en todos los grafos, confirmaremos que estas variables se carguen correctamente en el entorno de ejecución.

## Patrones de Integración

### 1. Configuración de Runnable para Trazabilidad

Todos los grafos deben configurarse para enviar trazas detalladas a LangSmith usando la siguiente estructura:

```python
# En archivo donde se compila e inicializa el grafo
from langchain.callbacks.tracers.langchain import LangChainTracer
from langchain.callbacks.tracers.langsmith import LangSmithTracer

# Configuración básica del grafo
graph = StateGraph(...)
# Agregar nodos, bordes, etc...

# Compilación con trazas detalladas
compiled_graph = graph.compile(
    checkpointer=RedisSaver(
        redis_url="redis://localhost:6379/0",  # Configurar según entorno
        namespace="github_import",             # Namespace específico por funcionalidad
    ),
    # Opcional: Tracer adicional si se necesita más control
    # tracer=LangSmithTracer(
    #     project_name="ai-agent-3-specialization"  # Usar variable de entorno
    # )
)
```

### 2. RunnableConfig por Invocación

Cada vez que se invoque un grafo, se debe pasar un `RunnableConfig` con metadatos detallados:

```python
# En función que ejecuta el grafo (ej: en una API endpoint)
from langchain.callbacks.manager import CallbackManagerForChainRun
from uuid import uuid4

async def import_github_project(github_url: str, user_id: str):
    # Generar un ID único para la ejecución o usar ID existente
    thread_id = f"github_import_{uuid4().hex}"
    # thread_id también puede ser basado en IDs existentes, ej: f"user_{user_id}_repo_{repo_id}"
    
    # Configuración para la ejecución
    run_config = {
        "configurable": {
            "thread_id": thread_id,  # Crucial para persistencia de checkpoints
        },
        "metadata": {
            "user_id": user_id,
            "github_url": github_url,
            "operation_type": "github_import",
            # Más metadatos relevantes para filtrar en LangSmith
        },
        "run_name": f"GitHub Import: {github_url.split('/')[-1]}",  # Nombre descriptivo
        "tags": ["github_import", "production"],  # Tags para agrupar ejecuciones
    }
    
    # Ejecutar el grafo con esta configuración
    result = await import_github_project_graph.ainvoke(
        {"github_url": github_url},
        config=run_config
    )
    
    return {"result": result, "thread_id": thread_id}
```

### 3. Estructura Consistente por Tipo de Grafo

Para mantener coherencia y facilitar la búsqueda en LangSmith, se seguirán estas convenciones:

| Tipo de Grafo | Prefijo `thread_id` | Tags Recomendados | Metadatos Comunes |
|---------------|---------------------|-------------------|-------------------|
| Importación GitHub | `github_import_` | `["github", "import"]` | `github_url`, `user_id` |
| Creación de Tareas | `task_create_` | `["task", "create"]` | `project_id`, `user_id` |
| Actualización de Proyecto | `project_update_` | `["project", "update"]` | `project_id`, `user_id` |
| Agente de Investigación | `research_` | `["research", "agent"]` | `query`, `user_id` |

### 4. Nodos con Trazabilidad Específica

Para nodos importantes o costosos (como interacciones con LLMs o APIs externas), añadiremos trazabilidad adicional:

```python
# Dentro de un nodo de LangGraph
async def analyze_repo_with_llm_node(state: State, config: RunnableConfig) -> State:
    # Extraer metadatos para enriquecer la traza
    github_url = state["github_url"]
    repo_name = github_url.split("/")[-1]
    
    # Configurar con metadatos extendidos 
    extended_config = {
        **config,
        "metadata": {
            **(config.get("metadata", {})),
            "repo_name": repo_name,
            "node": "analyze_repo_with_llm",
        },
        "tags": [*config.get("tags", []), "llm_analysis"],
    }
    
    # Llamada al LLM con trazabilidad extendida
    llm_result = await llm.ainvoke(
        prompt_template.format(repo_data=state["repo_data"]),
        config=extended_config,
    )
    
    # Actualizar estado
    return {
        **state,
        "llm_analysis": llm_result,
    }
```

### 5. Recuperación de IDs de Ejecución para Referencias Cruzadas

Para mantener trazabilidad entre ejecuciones relacionadas:

```python
# Capturar ID de traza de LangSmith para referencias cruzadas
from langchain.callbacks.tracers import LangChainTracer

async def execute_graph_with_tracing(graph, inputs, config):
    tracer = LangChainTracer(project_name="ai-agent-3-specialization")
    
    # Configurar con el tracer específico
    config_with_tracer = {**config, "callbacks": [tracer]}
    
    # Ejecutar grafo
    result = await graph.ainvoke(inputs, config=config_with_tracer)
    
    # Recuperar ID para referencias cruzadas
    run_id = tracer.latest_run.id if tracer.latest_run else None
    
    return result, run_id
```

## Implementación en Grafos Específicos

### Grafo de Importación de GitHub

Ejemplo de configuración específica para el grafo de importación:

```python
# En github_import_graph.py
import os
from langchain.callbacks.tracers.langchain import LangChainTracer

# Traceo específico del proyecto
project_name = os.getenv("LANGSMITH_PROJECT", "ai-agent-3-specialization")

# Nodos con trazabilidad específica para este flujo
async def fetch_github_repo_data_node(state: State, config: RunnableConfig) -> State:
    # Configuración específica para la llamada a GitHub
    github_config = {
        **config,
        "run_name": f"GitHub API: Fetch {state['github_url']}",
        "tags": [*config.get("tags", []), "github_api"],
    }
    
    # Resto de implementación...
```

## Uso de LangSmith para Análisis y Depuración

### Paneles y Vistas Recomendadas

1. **Vista de Grafos por Tipo**: Crear vistas filtradas por tags (`github_import`, `task_create`, etc.)
2. **Análisis de Latencia**: Monitorear tiempo de respuesta de nodos críticos, especialmente llamadas a API de GitHub o LLMs
3. **Dashboard de Errores**: Vista específica para identificar patrones de error comunes

### Mejores Prácticas para Debugging

1. Usar `tags` y `metadata` consistentemente para poder filtrar eficazmente
2. Monitorear especialmente nodos que interactúan con servicios externos
3. Capturar entradas y salidas de nodos complejos para análisis posterior

## Conclusión

La integración con LangSmith es esencial para mantener trazabilidad y observabilidad en un sistema basado en LangGraph, especialmente para flujos complejos como la importación de proyectos de GitHub. Siguiendo estos patrones, aseguramos consistencia con el repositorio original y facilitamos el debugging y optimización del sistema.
