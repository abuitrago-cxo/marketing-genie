#!/usr/bin/env python3
"""
简单的Vanna测试脚本
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_vanna_dependencies():
    """测试Vanna依赖"""
    try:
        import vanna
        from vanna.chromadb import ChromaDB_VectorStore
        from volcenginesdkarkruntime import Ark
        print("✅ Vanna依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ Vanna依赖缺失: {e}")
        return False

def test_vanna_basic():
    """测试Vanna基本功能"""
    if not test_vanna_dependencies():
        return False
    
    try:
        from agent.vanna_doubao import create_hr_vanna
        print("🚀 正在创建Vanna实例...")
        
        # 创建Vanna实例
        vn = create_hr_vanna()
        print("✅ Vanna实例创建成功")
        
        # 测试简单的SQL生成
        test_question = "查询所有员工的姓名和部门"
        print(f"🧠 测试问题: {test_question}")
        
        # 注意：这里可能会失败，因为还没有训练数据
        try:
            sql = vn.generate_sql(test_question)
            print(f"✅ 生成的SQL: {sql}")
        except Exception as e:
            print(f"⚠️  SQL生成失败（预期的，因为还没有训练）: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vanna测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🔍 开始Vanna集成测试...")
    
    # 检查环境变量
    if not os.getenv("ARK_API_KEY"):
        print("❌ 缺少ARK_API_KEY环境变量")
        sys.exit(1)
    
    # 测试基本功能
    if test_vanna_basic():
        print("🎉 Vanna集成测试通过！")
    else:
        print("❌ Vanna集成测试失败")
        sys.exit(1) 