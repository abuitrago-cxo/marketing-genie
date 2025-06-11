"""
Workflow Logging Module

Este módulo proporciona funciones para registrar eventos, métricas y resultados de la ejecución
de los workflows de agentes especializados.
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from langsmith import Client as LangsmithClient
from pydantic import BaseModel, Field

class WorkflowExecution(BaseModel):
    """Modelo para almacenar datos de ejecución de workflow."""
    query: str = Field(description="Consulta del usuario")
    timestamp: str = Field(description="Timestamp de la ejecución")
    workflow_id: str = Field(description="Identificador único del workflow")
    final_answer: str = Field(description="Respuesta final generada")
    quality_score: float = Field(description="Puntuación de calidad", ge=0, le=10)
    duration_seconds: float = Field(description="Duración en segundos")
    user_id: Optional[str] = Field(None, description="ID del usuario (si está disponible)")
    trace_id: Optional[str] = Field(None, description="ID de traza en LangSmith (si está disponible)")
    citations: List[Dict[str, Any]] = Field(default_factory=list, description="Citas de fuentes")
    
# Directorio para almacenar logs
_LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(_LOG_DIR, exist_ok=True)

async def log_workflow_execution(
    query: str, 
    result: Dict[str, Any],
    user_id: Optional[str] = None
) -> None:
    """
    Registra la ejecución de un workflow de agentes especializados.
    
    Args:
        query: La consulta original del usuario
        result: Resultado del workflow, incluyendo respuesta final, puntuaciones, etc.
        user_id: ID opcional del usuario
    """
    try:
        # Crear objeto de ejecución
        now = datetime.now()
        workflow_execution = WorkflowExecution(
            query=query,
            timestamp=now.isoformat(),
            workflow_id=f"wf-{now.timestamp()}",
            final_answer=result.get("final_answer", ""),
            quality_score=result.get("quality_score", 0.0),
            duration_seconds=result.get("execution_metrics", {}).get("total_duration_seconds", 0.0),
            user_id=user_id,
            trace_id=result.get("trace_id"),
            citations=result.get("citations", [])
        )
        
        # Guardar en archivo de log
        log_file = os.path.join(_LOG_DIR, f"workflow_logs_{now.strftime('%Y%m%d')}.jsonl")
        with open(log_file, "a") as f:
            f.write(workflow_execution.model_dump_json() + "\n")
            
        # Si hay un cliente LangSmith disponible y un trace_id, añadir feedback
        if "trace_id" in result and result["trace_id"]:
            try:
                langsmith_api_key = os.environ.get("LANGSMITH_API_KEY")
                if langsmith_api_key:
                    client = LangsmithClient()
                    client.create_feedback(
                        run_id=result["trace_id"],
                        key="quality_score",
                        score=float(result.get("quality_score", 0.0)),
                        comment=f"Automated quality assessment: {result.get('quality_score', 0.0)}/10"
                    )
            except Exception as e:
                print(f"Error adding LangSmith feedback: {e}")
                
        print(f"✅ Workflow execution logged: {workflow_execution.workflow_id}")
        return workflow_execution.workflow_id
        
    except Exception as e:
        print(f"❌ Error logging workflow execution: {e}")
        return None
