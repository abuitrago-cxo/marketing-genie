"""
自定义Vanna实现，集成豆包模型
这个类将Vanna的SQL生成能力与豆包模型结合，为HR数据库查询提供智能SQL生成
"""

import os
from typing import List, Dict, Any, Optional
from vanna.base import VannaBase
from vanna.chromadb import ChromaDB_VectorStore
from volcenginesdkarkruntime import Ark
import json
import atexit

class DoubaoVanna(ChromaDB_VectorStore, VannaBase):
    """
    继承Vanna的基础能力，使用豆包作为LLM，ChromaDB作为向量存储
    这就像是把豆包的大脑装进Vanna的身体里
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls, config: Dict[str, Any] = None):
        """实现单例模式，防止Context leak"""
        if cls._instance is None:
            cls._instance = super(DoubaoVanna, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: Dict[str, Any] = None):
        if self._initialized:
            return
            
        try:
            # 初始化向量数据库
            ChromaDB_VectorStore.__init__(self, config=config)
            VannaBase.__init__(self, config=config)
            
            # 配置豆包客户端
            self.ark_client = Ark(
                api_key=os.getenv("ARK_API_KEY"),
                timeout=config.get('timeout', 300) if config else 300
            )
            
            # 配置使用的豆包模型
            self.model_name = config.get('model', 'doubao-pro-256k-241115') if config else 'doubao-pro-256k-241115'
            
            # 注册清理函数
            atexit.register(self._cleanup)
            
            self._initialized = True
            print(f"✅ Vanna初始化完成，使用模型: {self.model_name}")
            
        except Exception as e:
            print(f"❌ Vanna初始化失败: {e}")
            raise
    
    def _cleanup(self):
        """清理资源，防止Context leak"""
        try:
            if hasattr(self, 'chroma_client'):
                # 清理ChromaDB连接
                pass
            print("🧹 Vanna资源清理完成")
        except Exception as e:
            print(f"⚠️ Vanna清理过程中出现异常: {e}")
    
    def system_message(self, message: str) -> dict:
        """定义系统消息格式"""
        return {"role": "system", "content": message}

    def user_message(self, message: str) -> dict:
        """定义用户消息格式"""
        return {"role": "user", "content": message}

    def assistant_message(self, message: str) -> dict:
        """定义助手消息格式"""
        return {"role": "assistant", "content": message}

    def submit_prompt(self, prompt: List[Dict], **kwargs) -> str:
        """
        使用豆包模型处理prompt
        这是Vanna调用LLM的核心接口，我们用豆包来实现
        """
        try:
            print("🤖 [Vanna-豆包] 正在处理SQL生成请求...")
            
            # 打印完整的SQL Prompt以便调试
            print("SQL Prompt:", prompt[:2] if len(prompt) > 2 else prompt)
            
            # 调用豆包API
            response = self.ark_client.chat.completions.create(
                model=self.model_name,
                messages=prompt,
                temperature=kwargs.get('temperature', 0.0),
                max_tokens=kwargs.get('max_tokens', 2000)
            )
            
            result = response.choices[0].message.content
            print(f"✅ [Vanna-豆包] SQL生成完成，响应长度: {len(result)}")
            print(f"LLM Response: {result}")
            
            return result
            
        except Exception as e:
            print(f"❌ [Vanna-豆包] API调用失败: {e}")
            raise

    def generate_sql(self, question: str, **kwargs) -> str:
        """
        重写SQL生成方法，添加更多的中文和业务逻辑优化
        """
        try:
            # 构建更适合中文HR查询的prompt
            enhanced_question = self._enhance_question_for_hr_context(question)
            
            # 调用父类的生成方法
            sql = super().generate_sql(enhanced_question, **kwargs)
            
            # 后处理SQL以确保适配我们的数据库
            validated_sql = self._validate_and_clean_sql(sql)
            
            print(f"✅ [Vanna-SQL生成] SQL生成成功:\n   {validated_sql}")
            
            return validated_sql
            
        except Exception as e:
            print(f"❌ [Vanna查询错误] 智能查询失败: {e}")
            raise
    
    def _enhance_question_for_hr_context(self, question: str) -> str:
        """
        为HR业务场景增强问题描述
        这就像给问题添加更多的上下文信息，帮助模型更好地理解
        """
        enhanced = f"""
        这是一个关于字节跳动人力资源数据的查询问题。
        
        重要的数据库Schema信息：
        
        employees表字段：
        - id: 员工ID
        - name: 员工姓名  
        - email: 员工邮箱
        - department_id: 部门ID
        - position: 职位
        - hire_date: 入职日期
        - salary: 薪资金额 (注意：字段名是salary，不是salary_amount)
        - status: 员工状态 (active/inactive)
        
        departments表字段：
        - id: 部门ID
        - name: 部门名称
        - budget: 部门预算
        - head_id: 部门负责人ID
        - location: 部门所在地
        
        projects表字段：
        - id: 项目ID
        - name: 项目名称
        - start_date: 开始日期
        - end_date: 结束日期
        - budget: 项目预算
        - manager_id: 项目经理ID
        
        请注意：
        1. 薪资字段名是 salary，不是 salary_amount
        2. 日期格式为 YYYY-MM-DD
        3. 员工状态字段是 status，值为 'active' 或 'inactive'
        4. 所有金额都以人民币为单位
        
        用户问题：{question}
        
        请生成准确的SQL查询来回答这个问题。
        """
        return enhanced
    
    def _validate_and_clean_sql(self, sql: str) -> str:
        """
        验证和清理生成的SQL
        这是一个安全检查机制，确保SQL的质量和安全性
        """
        if not sql or not sql.strip():
            raise ValueError("生成的SQL为空")
        
        sql = sql.strip()
        
        # 移除可能的markdown格式
        if sql.startswith('```sql'):
            sql = sql[6:]
        elif sql.startswith('```'):
            sql = sql[3:]
        if sql.endswith('```'):
            sql = sql[:-3]
        
        sql = sql.strip()
        
        # 修正常见的字段名错误
        sql = sql.replace('salary_amount', 'salary')
        sql = sql.replace('employment_date', 'hire_date')
        sql = sql.replace('employee_status', 'status')
        
        print(f"Extracted SQL: {sql}")
        
        # 基本的安全检查
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        sql_upper = sql.upper()
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(f"SQL包含危险操作: {keyword}")
        
        if not sql_upper.startswith('SELECT'):
            raise ValueError("只允许SELECT查询")
        
        return sql

# 工厂函数，方便创建Vanna实例
def create_hr_vanna(config: Dict[str, Any] = None) -> DoubaoVanna:
    """
    创建HR专用的Vanna实例
    这个函数就像是一个专门的工厂，生产适合HR业务的Vanna实例
    """
    default_config = {
        'model': 'doubao-pro-256k-241115',
        'timeout': 300,
        'path': './vanna_chromadb',  # ChromaDB数据存储路径
    }
    
    if config:
        default_config.update(config)
    
    return DoubaoVanna(config=default_config) 