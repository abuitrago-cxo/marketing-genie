__test__ = False
import pytest
pytest.skip("Skipping import test script", allow_module_level=True)

"""
Script de verificación de importaciones para el sistema LangGraph

Este script prueba las importaciones clave para garantizar que todos los módulos
se puedan cargar correctamente sin errores de importación.
"""

import sys
import importlib
from typing import List, Dict, Any, Tuple
import os

print(" Iniciando verificación de importaciones para LangGraph API")
print(f" Python version: {sys.version}")
print(f" Working directory: {os.getcwd()}")
print(f" PYTHONPATH: {sys.path}")

def test_import(module_path: str) -> Tuple[bool, str]:
    """Intenta importar un módulo y devuelve el resultado"""
    try:
        module = importlib.import_module(module_path)
        return True, f" Imported successfully: {module_path}"
    except ImportError as e:
        return False, f" Import failed: {module_path} - Error: {str(e)}"
    except Exception as e:
        return False, f" Other error: {module_path} - {type(e).__name__}: {str(e)}"

# Lista de módulos para probar
modules_to_test = [
    # Módulos core
    "agent",
    "agent.app",
    
    # Módulos agent principales
    "agent.graph",
    "agent.configuration",
    "agent.multi_agent_graph",
    "agent.multi_agent_state",
    "agent.router",
    "agent.specialized_graph",
    "agent.specialized_state",
    "agent.tools_and_schemas",
    
    # Módulos API
    "api",
    "api.specialized_endpoints",
    "api.enhanced_endpoints",
    "api.github_endpoints",
    "api.mcp_registry_endpoints",
    "api.mcp_router",
    "api.projects_endpoints",
    "api.agents_endpoints",
    "api.research_results_endpoints",
    "api.threads_endpoints",
    "api.chat_endpoints",
]

# Resultados
results = []
success_count = 0
failure_count = 0

print("\n Pruebas de importación:")
print("=" * 70)

# Ejecutar las pruebas
for module in modules_to_test:
    success, message = test_import(module)
    results.append((module, success, message))
    if success:
        success_count += 1
    else:
        failure_count += 1
    print(message)

print("\n Resumen:")
print("=" * 70)
print(f"Total modules tested: {len(modules_to_test)}")
print(f" Successful imports: {success_count}")
print(f" Failed imports: {failure_count}")

if failure_count > 0:
    print("\n Diagnóstico de problemas comunes:")
    print("=" * 70)
    print("1. Verifique que PYTHONPATH incluya el directorio raíz del proyecto")
    print("2. Asegúrese de que todos los directorios tengan archivos __init__.py")
    print("3. Revise importaciones circulares en los módulos")
    print("4. Verifique que las dependencias requeridas estén instaladas")
    print("5. Confirme la estructura correcta del paquete Python")

    sys.exit(1)
else:
    print("\n ¡Todas las importaciones fueron exitosas!")
    sys.exit(0)
