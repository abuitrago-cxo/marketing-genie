#!/usr/bin/env python3
"""
Script de prueba para el sistema de chat inteligente con contexto del sistema.
Prueba las nuevas funcionalidades de acotaciones inteligentes basadas en el estado del sistema.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from agent.utils.prompt_personality import (
    get_system_context,
    generate_intelligent_suggestions,
    create_intelligent_system_message
)

async def test_system_context():
    """Prueba la obtención del contexto del sistema"""
    print("🔍 Probando obtención del contexto del sistema...")
    
    try:
        context = await get_system_context()
        print(f"✅ Contexto obtenido exitosamente:")
        print(f"   - Proyectos: {context['projects_count']}")
        print(f"   - Base de datos: {'✅ Conectada' if context['database_connected'] else '❌ Desconectada'}")
        print(f"   - Tipo de usuario: {context['user_type']}")
        print(f"   - Salud del sistema: {context['system_health']}")
        print(f"   - Actividad reciente: {len(context['recent_activity'])} elementos")
        return context
    except Exception as e:
        print(f"❌ Error obteniendo contexto: {e}")
        return None

def test_intelligent_suggestions():
    """Prueba la generación de sugerencias inteligentes"""
    print("\n💡 Probando generación de sugerencias inteligentes...")
    
    # Simular diferentes contextos
    test_contexts = [
        {
            "name": "Usuario nuevo sin proyectos",
            "context": {
                "projects_count": 0,
                "database_connected": True,
                "user_type": "new",
                "system_health": "healthy",
                "recent_activity": []
            },
            "user_message": "hola"
        },
        {
            "name": "Usuario con un proyecto",
            "context": {
                "projects_count": 1,
                "database_connected": True,
                "user_type": "returning",
                "system_health": "healthy",
                "recent_activity": [{"name": "Mi Proyecto", "type": "project"}]
            },
            "user_message": "¿qué puedes hacer?"
        },
        {
            "name": "Usuario power con múltiples proyectos",
            "context": {
                "projects_count": 8,
                "database_connected": True,
                "user_type": "power_user",
                "system_health": "healthy",
                "recent_activity": [
                    {"name": "Proyecto A", "type": "project"},
                    {"name": "Proyecto B", "type": "project"}
                ]
            },
            "user_message": "necesito ayuda"
        },
        {
            "name": "Sistema con problemas",
            "context": {
                "projects_count": 2,
                "database_connected": False,
                "user_type": "returning",
                "system_health": "degraded",
                "recent_activity": []
            },
            "user_message": "hola"
        }
    ]
    
    for test_case in test_contexts:
        print(f"\n📋 Caso: {test_case['name']}")
        suggestions = generate_intelligent_suggestions(
            test_case["context"], 
            test_case["user_message"]
        )
        print(f"Sugerencias generadas:")
        print(suggestions[:200] + "..." if len(suggestions) > 200 else suggestions)

async def test_intelligent_system_message():
    """Prueba la creación de mensajes de sistema inteligentes"""
    print("\n🤖 Probando creación de mensajes de sistema inteligentes...")
    
    try:
        # Probar con diferentes tipos de mensajes
        test_messages = [
            "hola",
            "¿qué puedes hacer?",
            "necesito ayuda con mi proyecto",
            "quiero crear un nuevo proyecto"
        ]
        
        for user_msg in test_messages:
            print(f"\n📝 Mensaje del usuario: '{user_msg}'")
            
            try:
                intelligent_msg = await create_intelligent_system_message(
                    interaction_type="general_chat",
                    personality_type="proactive",
                    user_message=user_msg
                )
                
                # Mostrar solo una parte del mensaje para no saturar la salida
                preview = intelligent_msg[:300] + "..." if len(intelligent_msg) > 300 else intelligent_msg
                print(f"✅ Mensaje inteligente generado (preview):")
                print(preview)
                
            except Exception as e:
                print(f"❌ Error generando mensaje inteligente: {e}")
                
    except Exception as e:
        print(f"❌ Error en test de mensajes inteligentes: {e}")

async def test_database_connectivity():
    """Prueba la conectividad con la base de datos"""
    print("\n🗄️ Probando conectividad con la base de datos...")
    
    try:
        from api.projects_endpoints import get_db_connection, release_db_connection
        
        conn = await get_db_connection()
        if conn:
            print("✅ Conexión a la base de datos exitosa")
            
            # Probar consulta básica
            try:
                result = await conn.fetchval("SELECT COUNT(*) FROM projects")
                print(f"✅ Consulta exitosa: {result} proyectos encontrados")
                await release_db_connection(conn)
            except Exception as query_error:
                print(f"❌ Error en consulta: {query_error}")
                await release_db_connection(conn)
        else:
            print("❌ No se pudo establecer conexión con la base de datos")
            
    except Exception as e:
        print(f"❌ Error de conectividad: {e}")

async def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas del sistema de chat inteligente")
    print("=" * 60)
    
    # Verificar variables de entorno
    print("🔧 Verificando configuración...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    postgres_uri = os.getenv("POSTGRES_URI")
    
    print(f"   - GEMINI_API_KEY: {'✅ Configurada' if gemini_key else '❌ No configurada'}")
    print(f"   - POSTGRES_URI: {'✅ Configurada' if postgres_uri else '❌ No configurada'}")
    
    # Ejecutar pruebas
    await test_database_connectivity()
    context = await test_system_context()
    test_intelligent_suggestions()
    await test_intelligent_system_message()
    
    print("\n" + "=" * 60)
    print("🎉 Pruebas completadas")
    
    if context and context.get("database_connected"):
        print("✅ Sistema listo para generar acotaciones inteligentes")
    else:
        print("⚠️ Sistema funcionará con capacidades limitadas (sin base de datos)")

if __name__ == "__main__":
    asyncio.run(main())
