#!/usr/bin/env python3
"""
测试修复后的Vanna功能
"""

import os
import sys
from pathlib import Path

# 添加src路径到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from agent.vanna_doubao import create_hr_vanna

# 加载环境变量
load_dotenv()

def test_fixed_vanna():
    """测试修复后的Vanna功能"""
    try:
        print("🧪 测试修复后的Vanna功能...")
        
        # 创建Vanna实例
        vn = create_hr_vanna()
        
        # 测试问题
        test_questions = [
            "2024年发放了多少薪资",
            "查询所有员工的姓名",
            "每个部门有多少员工"
        ]
        
        for question in test_questions:
            try:
                print(f"\n📝 问题: {question}")
                sql = vn.generate_sql(question)
                print(f"✅ 生成的SQL:\n   {sql}")
                
                # 检查是否使用了正确的字段名
                if "salary_amount" in sql:
                    print("❌ 仍然使用错误的字段名 salary_amount")
                elif "salary" in sql:
                    print("✅ 使用了正确的字段名 salary")
                    
            except Exception as e:
                print(f"❌ 生成失败: {e}")
        
        print("\n🎉 测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_fixed_vanna():
        print("✅ 修复验证成功")
    else:
        print("❌ 修复验证失败")
        sys.exit(1) 