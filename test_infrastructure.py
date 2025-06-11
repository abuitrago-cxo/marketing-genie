#!/usr/bin/env python3
"""
Test simple de infraestructura PostgreSQL y Redis
"""

import asyncio
import os
import sys
from pathlib import Path

# Add backend src to path
backend_src = Path(__file__).parent / "backend" / "src"
sys.path.insert(0, str(backend_src))

async def test_postgresql():
    """Test PostgreSQL connectivity"""
    print("🔍 Testing PostgreSQL connectivity...")
    
    # URIs to try (following original repo pattern)
    postgres_uris = [
        "postgres://postgres:postgres@localhost:5433/postgres?sslmode=disable",  # Docker external
        "postgres://postgres:postgres@langgraph-postgres:5432/postgres?sslmode=disable",  # Docker internal
    ]
    
    for uri in postgres_uris:
        try:
            import asyncpg
            print(f"   Trying: {uri}")
            conn = await asyncpg.connect(uri)
            
            # Test basic query
            result = await conn.fetchval("SELECT 1")
            if result == 1:
                print(f"   ✅ PostgreSQL OK with {uri}")
                
                # Test if projects table exists
                try:
                    count = await conn.fetchval("SELECT COUNT(*) FROM projects")
                    print(f"   📊 Projects in database: {count}")
                except Exception as e:
                    print(f"   ⚠️ Projects table issue: {e}")
                
                await conn.close()
                return True
            
        except Exception as e:
            print(f"   ❌ Failed with {uri}: {e}")
            continue
    
    print("❌ PostgreSQL: All connection attempts failed")
    return False

def test_redis():
    """Test Redis connectivity"""
    print("🔍 Testing Redis connectivity...")
    
    redis_uris = [
        "redis://localhost:6379",  # Docker external
        "redis://langgraph-redis:6379",  # Docker internal
    ]
    
    for uri in redis_uris:
        try:
            import redis
            print(f"   Trying: {uri}")
            client = redis.from_url(uri, decode_responses=True)
            
            # Test ping
            result = client.ping()
            if result:
                print(f"   ✅ Redis OK with {uri}")
                client.close()
                return True
                
        except Exception as e:
            print(f"   ❌ Failed with {uri}: {e}")
            continue
    
    print("❌ Redis: All connection attempts failed")
    return False

async def test_intelligent_chat():
    """Test intelligent chat system"""
    print("🔍 Testing intelligent chat system...")
    
    try:
        from agent.utils.prompt_personality import get_system_context
        context = await get_system_context()
        
        print(f"   📊 System Context:")
        print(f"      - Projects: {context['projects_count']}")
        print(f"      - DB Connected: {context['database_connected']}")
        print(f"      - User Type: {context['user_type']}")
        print(f"      - System Health: {context['system_health']}")
        
        if context['database_connected']:
            print("   ✅ Intelligent chat can access database")
            return True
        else:
            print("   ⚠️ Intelligent chat working in degraded mode")
            return False
            
    except Exception as e:
        print(f"   ❌ Intelligent chat error: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("🔍 Checking environment variables...")
    
    required_vars = ['GEMINI_API_KEY', 'LANGSMITH_API_KEY']
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: Configured")
        else:
            print(f"   ❌ {var}: Not configured")
            all_good = False
    
    return all_good

async def main():
    """Main test function"""
    print("🚀 Testing Infrastructure Status")
    print("=" * 50)
    
    # Test environment
    env_ok = check_environment()
    
    # Test databases
    postgres_ok = await test_postgresql()
    redis_ok = test_redis()
    
    # Test intelligent chat
    chat_ok = await test_intelligent_chat()
    
    print("\n" + "=" * 50)
    print("📊 INFRASTRUCTURE STATUS SUMMARY")
    print(f"   Environment Variables: {'✅ OK' if env_ok else '❌ FAIL'}")
    print(f"   PostgreSQL: {'✅ OK' if postgres_ok else '❌ FAIL'}")
    print(f"   Redis: {'✅ OK' if redis_ok else '❌ FAIL'}")
    print(f"   Intelligent Chat: {'✅ OK' if chat_ok else '⚠️ DEGRADED'}")
    
    if postgres_ok and redis_ok and chat_ok:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("✅ Your intelligent chat system is ready with full database support")
        return 0
    elif env_ok:
        print("\n⚠️ PARTIAL FUNCTIONALITY")
        print("✅ Basic system works, but database features are limited")
        return 0
    else:
        print("\n❌ SYSTEM ISSUES DETECTED")
        print("🔧 Check Docker services and environment configuration")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test error: {e}")
        sys.exit(1)
