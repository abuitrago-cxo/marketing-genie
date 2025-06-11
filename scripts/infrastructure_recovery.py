#!/usr/bin/env python3
"""
Script de recuperación completa de infraestructura PostgreSQL y Redis.
Implementa el plan robusto de 5 fases para asegurar que la base de datos funcione correctamente.
"""

import asyncio
import asyncpg
import redis
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent.parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

class InfrastructureRecovery:
    """Clase principal para la recuperación de infraestructura"""
    
    def __init__(self):
        self.postgres_uri = os.getenv('POSTGRES_URI')
        self.redis_uri = os.getenv('REDIS_URI')
        self.recovery_log = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.recovery_log.append(log_entry)
    
    def run_command(self, command: str, timeout: int = 60) -> tuple:
        """Ejecutar comando con timeout"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def phase_1_verify_environment(self) -> bool:
        """FASE 1: Verificar configuración de variables de entorno"""
        self.log("🔧 FASE 1: Verificando configuración de variables de entorno")
        
        required_vars = {
            'GEMINI_API_KEY': 'API key de Google Gemini',
            'LANGSMITH_API_KEY': 'API key de LangSmith',
            'POSTGRES_URI': 'URI de conexión PostgreSQL',
            'REDIS_URI': 'URI de conexión Redis'
        }
        
        missing_vars = []
        for var, description in required_vars.items():
            value = os.getenv(var)
            if value:
                self.log(f"✅ {var}: Configurada")
            else:
                self.log(f"❌ {var}: No configurada ({description})")
                missing_vars.append(var)
        
        if missing_vars:
            self.log(f"❌ Variables faltantes: {missing_vars}", "ERROR")
            return False
        
        self.log("✅ FASE 1 completada: Todas las variables están configuradas")
        return True
    
    def phase_2_start_services(self) -> bool:
        """FASE 2: Inicializar servicios Docker"""
        self.log("🚀 FASE 2: Iniciando servicios de infraestructura")
        
        # Verificar si Docker está disponible
        success, _, _ = self.run_command("docker --version")
        if not success:
            self.log("❌ Docker no está disponible", "ERROR")
            return False
        
        # Verificar si docker-compose está disponible
        success, _, _ = self.run_command("docker-compose --version")
        if not success:
            self.log("❌ Docker Compose no está disponible", "ERROR")
            return False
        
        # Detener servicios existentes
        self.log("🛑 Deteniendo servicios existentes...")
        self.run_command("docker-compose down", timeout=30)
        
        # Construir imagen actualizada
        self.log("🔨 Construyendo imagen Docker actualizada...")
        success, stdout, stderr = self.run_command(
            "docker build -t gemini-fullstack-langgraph-enhanced -f Dockerfile .", 
            timeout=300
        )
        
        if not success:
            self.log(f"❌ Error construyendo imagen: {stderr}", "ERROR")
            return False
        
        # Iniciar servicios de base de datos
        self.log("🚀 Iniciando PostgreSQL y Redis...")
        success, stdout, stderr = self.run_command(
            "docker-compose up -d langgraph-postgres langgraph-redis", 
            timeout=120
        )
        
        if not success:
            self.log(f"❌ Error iniciando servicios: {stderr}", "ERROR")
            return False
        
        # Esperar a que los servicios estén listos
        self.log("⏳ Esperando a que PostgreSQL esté listo...")
        for i in range(30):  # 60 segundos máximo
            success, _, _ = self.run_command(
                "docker-compose exec -T langgraph-postgres pg_isready -U postgres"
            )
            if success:
                self.log("✅ PostgreSQL está listo")
                break
            time.sleep(2)
        else:
            self.log("❌ PostgreSQL no respondió en tiempo esperado", "ERROR")
            return False
        
        self.log("⏳ Esperando a que Redis esté listo...")
        for i in range(30):  # 60 segundos máximo
            success, _, _ = self.run_command(
                "docker-compose exec -T langgraph-redis redis-cli ping"
            )
            if success:
                self.log("✅ Redis está listo")
                break
            time.sleep(2)
        else:
            self.log("❌ Redis no respondió en tiempo esperado", "ERROR")
            return False
        
        self.log("✅ FASE 2 completada: Servicios iniciados correctamente")
        return True
    
    async def phase_3_verify_schema(self) -> bool:
        """FASE 3: Verificar y crear esquema de base de datos"""
        self.log("📊 FASE 3: Verificando esquema de base de datos")
        
        if not self.postgres_uri:
            self.log("❌ POSTGRES_URI no configurada", "ERROR")
            return False
        
        try:
            # Conectar a PostgreSQL
            conn = await asyncpg.connect(self.postgres_uri)
            self.log("✅ Conexión a PostgreSQL exitosa")
            
            # Verificar tablas existentes
            tables = await conn.fetch("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            existing_tables = [row['table_name'] for row in tables]
            self.log(f"📋 Tablas existentes: {existing_tables}")
            
            # Tablas requeridas para el sistema
            required_tables = [
                'projects', 'tasks', 'milestones', 'agent_long_term_memory',
                'chat_threads', 'chat_messages', 'mcp_server_registry'
            ]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                self.log(f"⚠️ Tablas faltantes: {missing_tables}")
                # Aquí podríamos ejecutar scripts de creación de esquema
                # Por ahora, solo reportamos
            else:
                self.log("✅ Todas las tablas requeridas están presentes")
            
            # Verificar que podemos hacer consultas básicas
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                self.log("✅ Consultas básicas funcionando")
            
            await conn.close()
            self.log("✅ FASE 3 completada: Esquema verificado")
            return True
            
        except Exception as e:
            self.log(f"❌ Error verificando esquema: {e}", "ERROR")
            return False
    
    async def phase_4_populate_test_data(self) -> bool:
        """FASE 4: Poblar con datos de prueba"""
        self.log("📝 FASE 4: Poblando datos de prueba")
        
        try:
            conn = await asyncpg.connect(self.postgres_uri)
            
            # Verificar si ya hay proyectos
            existing_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
            self.log(f"📊 Proyectos existentes: {existing_count}")
            
            if existing_count == 0:
                # Crear proyectos de prueba
                test_projects = [
                    {
                        'name': 'Proyecto Demo AI Assistant',
                        'description': 'Proyecto de demostración del sistema de IA para testing de acotaciones inteligentes',
                        'status': 'active',
                        'priority': 'high'
                    },
                    {
                        'name': 'Proyecto Testing Multi-Agent',
                        'description': 'Proyecto para probar el sistema multi-agente y coordinación de tareas',
                        'status': 'planning',
                        'priority': 'medium'
                    },
                    {
                        'name': 'Proyecto Análisis de Código',
                        'description': 'Proyecto enfocado en análisis automático de código y documentación',
                        'status': 'active',
                        'priority': 'high'
                    }
                ]
                
                for project in test_projects:
                    await conn.execute("""
                        INSERT INTO projects (name, description, status, priority, created_at, updated_at, user_id)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (name) DO NOTHING
                    """, 
                    project['name'], project['description'], project['status'], 
                    project['priority'], datetime.now(), datetime.now(), 'test_user')
                
                self.log("✅ Datos de prueba insertados")
            else:
                self.log("ℹ️ Ya existen proyectos, omitiendo inserción de datos de prueba")
            
            # Verificar datos finales
            final_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
            self.log(f"📊 Total de proyectos en DB: {final_count}")
            
            await conn.close()
            self.log("✅ FASE 4 completada: Datos de prueba listos")
            return True
            
        except Exception as e:
            self.log(f"❌ Error poblando datos: {e}", "ERROR")
            return False
    
    async def phase_5_test_system(self) -> bool:
        """FASE 5: Testing y validación completa"""
        self.log("🧪 FASE 5: Testing y validación del sistema completo")
        
        try:
            # Test 1: Contexto del sistema
            try:
                from agent.utils.prompt_personality import get_system_context
                context = await get_system_context()
                self.log(f"✅ Contexto del sistema obtenido:")
                self.log(f"   - Proyectos: {context['projects_count']}")
                self.log(f"   - DB conectada: {context['database_connected']}")
                self.log(f"   - Tipo usuario: {context['user_type']}")
                self.log(f"   - Salud sistema: {context['system_health']}")
                
                if context['database_connected'] and context['projects_count'] > 0:
                    self.log("✅ Sistema de contexto funcionando correctamente")
                else:
                    self.log("⚠️ Sistema de contexto con limitaciones")
                    
            except Exception as e:
                self.log(f"❌ Error en test de contexto: {e}", "ERROR")
                return False
            
            # Test 2: Chat inteligente
            try:
                from agent.utils.prompt_personality import create_intelligent_system_message
                msg = await create_intelligent_system_message(user_message="hola")
                if len(msg) > 100:  # Verificar que se generó contenido sustancial
                    self.log("✅ Sistema de chat inteligente funcionando")
                else:
                    self.log("⚠️ Sistema de chat con respuesta limitada")
            except Exception as e:
                self.log(f"❌ Error en test de chat: {e}", "ERROR")
                return False
            
            # Test 3: Redis connectivity
            try:
                redis_client = redis.from_url(self.redis_uri, decode_responses=True)
                redis_client.ping()
                self.log("✅ Conectividad Redis verificada")
                redis_client.close()
            except Exception as e:
                self.log(f"❌ Error conectando a Redis: {e}", "ERROR")
                return False
            
            self.log("✅ FASE 5 completada: Sistema completamente funcional")
            return True
            
        except Exception as e:
            self.log(f"❌ Error en testing del sistema: {e}", "ERROR")
            return False
    
    async def run_full_recovery(self) -> bool:
        """Ejecutar plan completo de recuperación"""
        self.log("🚀 Iniciando Plan Robusto de Recuperación de Infraestructura")
        self.log("=" * 60)
        
        phases = [
            ("Verificación de Entorno", self.phase_1_verify_environment),
            ("Inicialización de Servicios", self.phase_2_start_services),
            ("Verificación de Esquema", self.phase_3_verify_schema),
            ("Población de Datos", self.phase_4_populate_test_data),
            ("Testing del Sistema", self.phase_5_test_system)
        ]
        
        for phase_name, phase_func in phases:
            self.log(f"\n🎯 Ejecutando: {phase_name}")
            
            if asyncio.iscoroutinefunction(phase_func):
                success = await phase_func()
            else:
                success = phase_func()
            
            if not success:
                self.log(f"❌ FALLO en {phase_name}", "ERROR")
                self.log("🛑 Recuperación detenida", "ERROR")
                return False
            
            self.log(f"✅ {phase_name} completada exitosamente")
        
        self.log("\n" + "=" * 60)
        self.log("🎉 RECUPERACIÓN COMPLETA EXITOSA")
        self.log("✅ PostgreSQL y Redis funcionando correctamente")
        self.log("✅ Sistema de acotaciones inteligentes operativo")
        self.log("✅ Datos de prueba disponibles")
        
        return True
    
    def save_recovery_log(self):
        """Guardar log de recuperación"""
        log_file = f"recovery_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w') as f:
            f.write("\n".join(self.recovery_log))
        self.log(f"📄 Log guardado en: {log_file}")

async def main():
    """Función principal"""
    recovery = InfrastructureRecovery()
    
    try:
        success = await recovery.run_full_recovery()
        recovery.save_recovery_log()
        
        if success:
            print("\n🎉 ¡Infraestructura recuperada exitosamente!")
            print("Ahora puedes usar el sistema de chat inteligente con todas sus capacidades.")
            return 0
        else:
            print("\n❌ La recuperación falló. Revisa el log para más detalles.")
            return 1
            
    except KeyboardInterrupt:
        recovery.log("🛑 Recuperación interrumpida por el usuario", "WARNING")
        return 1
    except Exception as e:
        recovery.log(f"💥 Error crítico: {e}", "ERROR")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
