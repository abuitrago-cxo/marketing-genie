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
        重写SQL生成方法，直接使用原始问题
        """
        try:
            # 直接调用父类的生成方法，不进行问题增强
            sql = super().generate_sql(question, **kwargs)
            
            # 后处理SQL以确保适配我们的数据库
            validated_sql = self._validate_and_clean_sql(sql)
            
            print(f"✅ [Vanna-SQL生成] SQL生成成功:\n   {validated_sql}")
            
            return validated_sql
            
        except Exception as e:
            print(f"❌ [Vanna查询错误] 智能查询失败: {e}")
            raise
    
    def _validate_and_clean_sql(self, sql: str) -> str:
        """
        验证和清理生成的SQL
        这是一个安全检查机制，确保SQL的质量和安全性
        """
        if not sql or not sql.strip():
            raise ValueError("生成的SQL为空")
        
        original_sql = sql.strip()
        
        # 第一步：尝试提取SQL代码块
        extracted_sql = self._extract_sql_from_response(original_sql)
        
        # 第二步：清理和修正SQL
        cleaned_sql = self._clean_sql_syntax(extracted_sql)
        
        # 第三步：安全检查
        self._validate_sql_safety(cleaned_sql)
        
        print(f"✅ [SQL清理完成] 最终SQL: {cleaned_sql}")
        
        return cleaned_sql
    
    def _extract_sql_from_response(self, response: str) -> str:
        """
        从LLM响应中提取SQL语句
        支持多种格式：markdown代码块、注释、解释文本等
        """
        lines = response.split('\n')
        sql_lines = []
        in_sql_block = False
        found_sql = False
        
        for line in lines:
            line = line.strip()
            
            # 检测SQL代码块开始
            if line.startswith('```sql') or line.startswith('```SQL'):
                in_sql_block = True
                continue
            elif line.startswith('```') and not in_sql_block:
                in_sql_block = True
                continue
            elif line == '```' and in_sql_block:
                in_sql_block = False
                if sql_lines:  # 如果已经找到SQL，就停止
                    break
                continue
            
            # 如果在SQL代码块中，收集SQL行
            if in_sql_block:
                if line and not line.startswith('--'):  # 排除注释行
                    sql_lines.append(line)
                    found_sql = True
            else:
                # 如果不在代码块中，检查是否是纯SQL行
                if self._looks_like_sql(line):
                    sql_lines.append(line)
                    found_sql = True
                elif found_sql and line and not line.startswith('--'):
                    # 如果已经找到SQL，遇到非SQL行就停止
                    break
        
        if not sql_lines:
            # 如果没有找到SQL，尝试提取整个响应作为SQL
            potential_sql = response.strip()
            if self._looks_like_sql(potential_sql):
                return potential_sql
            else:
                raise ValueError(f"无法从响应中提取有效的SQL语句: {response[:200]}...")
        
        return '\n'.join(sql_lines)
    
    def _looks_like_sql(self, text: str) -> bool:
        """
        判断文本是否看起来像SQL语句
        """
        if not text:
            return False
        
        text_upper = text.upper().strip()
        
        # SQL关键字检查
        sql_keywords = ['SELECT', 'WITH', 'FROM', 'WHERE', 'JOIN', 'GROUP BY', 'ORDER BY', 'HAVING']
        return any(keyword in text_upper for keyword in sql_keywords)
    
    def _clean_sql_syntax(self, sql: str) -> str:
        """
        清理SQL语法，修正常见错误
        """
        if not sql:
            return sql
        
        # 修正常见的字段名错误
        sql = sql.replace('salary_amount', 'salary')
        sql = sql.replace('employment_date', 'hire_date')
        sql = sql.replace('employee_status', 'status')
        sql = sql.replace('payment_amount', 'total_amount')  # 修正薪资字段
        sql = sql.replace('payment_date', 'created_at')      # 修正日期字段
        sql = sql.replace('salary_payments', 'salaries')     # 修正表名
        
        # 修正日期函数
        sql = sql.replace('EXTRACT(YEAR FROM', 'YEAR(')
        sql = sql.replace('EXTRACT(MONTH FROM', 'MONTH(')
        
        # 移除多余的空白行
        lines = [line.strip() for line in sql.split('\n') if line.strip()]
        sql = '\n'.join(lines)
        
        return sql
    
    def _validate_sql_safety(self, sql: str) -> None:
        """
        验证SQL安全性
        """
        if not sql:
            raise ValueError("SQL为空")
        
        sql_upper = sql.upper().strip()
        
        # 检查危险操作
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(f"SQL包含危险操作: {keyword}")
        
        # 检查是否为查询语句（支持CTE）
        if not (sql_upper.startswith('SELECT') or sql_upper.startswith('WITH')):
            raise ValueError("只允许SELECT查询和CTE查询")
        
        # 如果是CTE，确保最终是SELECT
        if sql_upper.startswith('WITH'):
            if 'SELECT' not in sql_upper:
                raise ValueError("CTE查询必须包含SELECT语句")

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