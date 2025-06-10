"""
Vanna初始化脚本
在系统启动时运行一次，确保Vanna模型已经训练完成
"""

import os
from pathlib import Path
from agent.vanna_trainer import train_vanna_with_hr_data

def ensure_vanna_trained():
    """
    确保Vanna模型已经训练
    这个函数检查是否存在训练好的模型，如果没有就进行训练
    """
    
    # 检查Vanna数据目录是否存在
    vanna_data_path = Path("./vanna_chromadb")
    
    if not vanna_data_path.exists() or len(list(vanna_data_path.glob("*"))) == 0:
        print("🎓 检测到Vanna未训练，开始自动训练...")
        try:
            train_vanna_with_hr_data()
            print("✅ Vanna训练完成！")
        except Exception as e:
            print(f"❌ Vanna训练失败: {e}")
            print("⚠️  系统将继续运行，但可能无法使用Vanna智能SQL生成功能")
    else:
        print("✅ Vanna模型已存在，跳过训练")

def check_vanna_dependencies():
    """
    检查Vanna相关依赖是否正确安装
    """
    try:
        import vanna
        from vanna.chromadb import ChromaDB_VectorStore
        from volcenginesdkarkruntime import Ark
        print("✅ Vanna依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ Vanna依赖缺失: {e}")
        print("请运行: pip install 'vanna[chromadb]'")
        return False

if __name__ == "__main__":
    print("🚀 开始Vanna初始化检查...")
    
    # 检查依赖
    if check_vanna_dependencies():
        # 确保训练完成
        ensure_vanna_trained()
    else:
        print("❌ 由于依赖问题，跳过Vanna初始化")
    
    print("🎉 Vanna初始化检查完成") 