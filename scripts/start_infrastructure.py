#!/usr/bin/env python3
"""
Script simple para iniciar la infraestructura PostgreSQL y Redis
siguiendo exactamente el patrón del repositorio original.
"""

import subprocess
import time
import sys
import os

def run_command(command: str, timeout: int = 60) -> tuple:
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

def log(message: str):
    """Log simple con timestamp"""
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def verify_docker():
    """Verificar que Docker esté disponible"""
    log("🔧 Verificando Docker...")
    
    success, _, _ = run_command("docker --version")
    if not success:
        log("❌ Docker no está disponible")
        return False
    
    success, _, _ = run_command("docker-compose --version")
    if not success:
        log("❌ Docker Compose no está disponible")
        return False
    
    log("✅ Docker y Docker Compose disponibles")
    return True

def verify_env_vars():
    """Verificar variables de entorno requeridas"""
    log("🔧 Verificando variables de entorno...")
    
    required_vars = ['GEMINI_API_KEY', 'LANGSMITH_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        log(f"❌ Variables faltantes: {missing_vars}")
        return False
    
    log("✅ Variables de entorno configuradas")
    return True

def build_image():
    """Construir imagen Docker"""
    log("🔨 Construyendo imagen Docker...")
    
    success, stdout, stderr = run_command(
        "docker build -t gemini-fullstack-langgraph -f Dockerfile .", 
        timeout=300
    )
    
    if not success:
        log(f"❌ Error construyendo imagen: {stderr}")
        return False
    
    log("✅ Imagen Docker construida")
    return True

def start_services():
    """Iniciar servicios PostgreSQL y Redis"""
    log("🚀 Iniciando servicios PostgreSQL y Redis...")
    
    # Detener servicios existentes primero
    log("🛑 Deteniendo servicios existentes...")
    run_command("docker-compose down", timeout=30)
    
    # Iniciar solo PostgreSQL y Redis (como en el repo original)
    success, stdout, stderr = run_command(
        "docker-compose up -d langgraph-postgres langgraph-redis", 
        timeout=120
    )
    
    if not success:
        log(f"❌ Error iniciando servicios: {stderr}")
        return False
    
    log("✅ Servicios iniciados")
    return True

def wait_for_services():
    """Esperar a que los servicios estén listos"""
    log("⏳ Esperando a que PostgreSQL esté listo...")
    
    for i in range(30):  # 60 segundos máximo
        success, _, _ = run_command(
            "docker-compose exec -T langgraph-postgres pg_isready -U postgres"
        )
        if success:
            log("✅ PostgreSQL está listo")
            break
        time.sleep(2)
    else:
        log("❌ PostgreSQL no respondió en tiempo esperado")
        return False
    
    log("⏳ Esperando a que Redis esté listo...")
    for i in range(30):  # 60 segundos máximo
        success, _, _ = run_command(
            "docker-compose exec -T langgraph-redis redis-cli ping"
        )
        if success:
            log("✅ Redis está listo")
            break
        time.sleep(2)
    else:
        log("❌ Redis no respondió en tiempo esperado")
        return False
    
    return True

def verify_connectivity():
    """Verificar conectividad final"""
    log("🧪 Verificando conectividad...")
    
    # Test PostgreSQL
    success, _, _ = run_command(
        "docker-compose exec -T langgraph-postgres pg_isready -U postgres"
    )
    if success:
        log("✅ PostgreSQL: Conectividad OK")
    else:
        log("❌ PostgreSQL: Conectividad FAIL")
        return False
    
    # Test Redis
    success, _, _ = run_command(
        "docker-compose exec -T langgraph-redis redis-cli ping"
    )
    if success:
        log("✅ Redis: Conectividad OK")
    else:
        log("❌ Redis: Conectividad FAIL")
        return False
    
    return True

def start_full_application():
    """Iniciar aplicación completa (opcional)"""
    log("🚀 ¿Quieres iniciar la aplicación completa? (y/n)")
    
    # Para script automático, comentar esta línea y descomentar la siguiente
    # response = input().lower().strip()
    response = "n"  # Por defecto no iniciar app completa
    
    if response == "y":
        log("🚀 Iniciando aplicación completa...")
        success, stdout, stderr = run_command(
            "docker-compose up -d", 
            timeout=120
        )
        
        if success:
            log("✅ Aplicación completa iniciada")
            log("🌐 Frontend: http://localhost:8123/app/")
            log("🔧 API: http://localhost:8123")
            return True
        else:
            log(f"❌ Error iniciando aplicación: {stderr}")
            return False
    else:
        log("ℹ️ Solo servicios de base de datos iniciados")
        log("💡 Para iniciar la app completa: docker-compose up -d")
        return True

def main():
    """Función principal"""
    log("🚀 Iniciando infraestructura PostgreSQL y Redis")
    log("📋 Siguiendo patrón del repositorio original")
    log("=" * 50)
    
    steps = [
        ("Verificar Docker", verify_docker),
        ("Verificar Variables de Entorno", verify_env_vars),
        ("Construir Imagen", build_image),
        ("Iniciar Servicios", start_services),
        ("Esperar Servicios", wait_for_services),
        ("Verificar Conectividad", verify_connectivity),
        ("Configurar Aplicación", start_full_application)
    ]
    
    for step_name, step_func in steps:
        log(f"\n🎯 {step_name}...")
        
        if not step_func():
            log(f"❌ FALLO en {step_name}")
            log("🛑 Proceso detenido")
            return 1
        
        log(f"✅ {step_name} completado")
    
    log("\n" + "=" * 50)
    log("🎉 INFRAESTRUCTURA LISTA")
    log("✅ PostgreSQL funcionando en puerto 5433")
    log("✅ Redis funcionando en puerto 6379")
    log("✅ Sistema de acotaciones inteligentes puede usar la base de datos")
    
    log("\n📊 Comandos útiles:")
    log("  - Ver logs: docker-compose logs")
    log("  - Estado: docker-compose ps")
    log("  - Detener: docker-compose down")
    log("  - Reiniciar: docker-compose restart")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log("\n🛑 Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        log(f"\n💥 Error crítico: {e}")
        sys.exit(1)
