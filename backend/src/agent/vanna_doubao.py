"""
自定义Vanna实现，集成豆包模型
这个类将Vanna的SQL生成能力与豆包模型结合，为HR数据库查询提供智能SQL生成
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from vanna.base import VannaBase
from vanna.chromadb import ChromaDB_VectorStore
from volcenginesdkarkruntime import Ark
import atexit
from .prompts import database_query_instructions, get_current_date
from .database_schema import DATABASE_SCHEMA
from .tools_and_schemas import DatabaseQueryResult
from .database_tools import execute_database_query, format_query_result

class DoubaoVanna(ChromaDB_VectorStore, VannaBase):
    """
    继承Vanna的基础能力，使用豆包作为LLM，ChromaDB作为向量存储
    混合方案：使用Vanna的RAG获取相关上下文，然后用豆包传统方法生成JSON结果
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

    def generate_sql_with_rag_context(self, question: str, **kwargs) -> DatabaseQueryResult:
        """
        混合方案核心方法：使用Vanna RAG获取上下文，然后用豆包生成JSON结果
        """
        try:
            print(f"🔍 [混合方案] 开始处理问题: {question[:50]}...")
            
            # 步骤1: 使用Vanna的RAG能力获取相关上下文
            print("📚 [Vanna RAG] 正在获取相关上下文...")
            rag_context = self._get_rag_context(question)
            
            # 步骤2: 使用RAG上下文构建豆包提示词
            print("🔧 [构建提示词] 使用RAG上下文生成提示词...")
            custom_prompt = self._create_prompt_with_rag_context(question, rag_context)
            
            # 步骤3: 调用豆包API生成JSON格式结果
            print("🤖 [豆包生成] 正在生成JSON查询计划...")
            response = self.ark_client.chat.completions.create(
                model=self.model_name,
                messages=custom_prompt,
                temperature=0.0,
                max_tokens=2000
            )
            
            json_result = response.choices[0].message.content
            print(f"✅ [豆包生成] JSON生成完成，长度: {len(json_result)}")
            
            # 步骤4: 解析JSON结果
            parsed_result = self._parse_json_response(json_result)
            print(f"📊 [JSON解析] 成功解析，包含 {len(parsed_result.queries)} 个SQL查询")
            
            return parsed_result
                
        except Exception as e:
            print(f"❌ [混合方案错误] 处理失败: {e}")
            raise

    def _get_rag_context(self, question: str, top_k: int = 10) -> str:
        """
        使用Vanna的RAG能力获取与问题最相关的上下文信息
        """
        try:
            # 使用Vanna的相似性搜索获取相关文档
            print(f"🔎 [RAG搜索] 搜索与'{question}'相关的top-{top_k}上下文...")
            
            # 使用Vanna内建的similarity_search方法获取相关上下文
            related_ddl = []
            related_documentation = []
            related_sql = []
            
            try:
                # 尝试获取相关的DDL
                if hasattr(self, 'get_related_ddl'):
                    related_ddl = self.get_related_ddl(question, n_results=top_k)
                elif hasattr(self, 'similarity_search') and hasattr(self, 'ddl_collection'):
                    # 备用方案：直接使用similarity_search
                    ddl_results = self.similarity_search(question, collection_name="ddl", n_results=top_k)
                    related_ddl = [result for result in ddl_results] if ddl_results else []
            except Exception as e:
                print(f"⚠️ [DDL搜索] 获取DDL失败: {e}")
            
            try:
                # 尝试获取相关的文档
                if hasattr(self, 'get_related_documentation'):
                    related_documentation = self.get_related_documentation(question, n_results=top_k)
                elif hasattr(self, 'similarity_search'):
                    doc_results = self.similarity_search(question, collection_name="documentation", n_results=top_k)
                    related_documentation = [result for result in doc_results] if doc_results else []
            except Exception as e:
                print(f"⚠️ [文档搜索] 获取文档失败: {e}")
            
            try:
                # 尝试获取相关的SQL
                if hasattr(self, 'get_related_sql'):
                    related_sql = self.get_related_sql(question, n_results=top_k)
                elif hasattr(self, 'similarity_search'):
                    sql_results = self.similarity_search(question, collection_name="sql", n_results=top_k)
                    related_sql = [result for result in sql_results] if sql_results else []
            except Exception as e:
                print(f"⚠️ [SQL搜索] 获取SQL失败: {e}")
            
            # 构建RAG上下文
            rag_context_parts = []
            
            # 添加相关的表结构信息
            if related_ddl:
                rag_context_parts.append("🏗️ **相关数据表结构:**")
                for ddl in related_ddl:
                    rag_context_parts.append(f"```sql\n{ddl}\n```")
            
            # 添加相关的业务文档
            if related_documentation:
                rag_context_parts.append("\n📖 **相关业务知识:**")
                for doc in related_documentation:
                    rag_context_parts.append(f"• {doc}")
            
            # 添加相关的SQL样例
            if related_sql:
                rag_context_parts.append("\n💡 **相关查询样例:**")
                for sql in related_sql:
                    rag_context_parts.append(f"```sql\n{sql}\n```")
            
            rag_context = "\n".join(rag_context_parts)
            
            print(f"✅ [RAG搜索] 获取到 {len(related_ddl)} 个DDL，{len(related_documentation)} 个文档，{len(related_sql)} 个SQL样例")
            print(f"📋 [RAG上下文] 上下文长度: {len(rag_context)} 字符")
            
            # 如果没有RAG上下文，返回基础schema
            if not rag_context:
                print("⚠️ [RAG回退] 没有找到相关上下文，使用基础schema")
                return self._format_database_schema()
            
            return rag_context
            
        except Exception as e:
            print(f"⚠️ [RAG搜索] 获取上下文失败: {e}")
            # 如果RAG失败，返回基础schema信息
            print("🔄 [RAG回退] 使用完整schema作为上下文")
            return self._format_database_schema()

    def _create_prompt_with_rag_context(self, question: str, rag_context: str) -> List[Dict]:
        """
        使用RAG上下文创建豆包提示词，而不是完整的schema
        """
        # 使用database_query_instructions模板，但用RAG上下文替换完整schema
        system_message = database_query_instructions.format(
            database_schema=rag_context,  # 关键：使用RAG上下文替换完整schema
            current_date=get_current_date(),
            query_requirement=question
        )
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"用户查询需求: {question}"}
        ]
        
        print(f"🔧 [提示词构建] 使用RAG上下文构建database_query_instructions提示词")
        
        return messages

    def generate_sql(self, question: str, **kwargs) -> str:
        """
        保持Vanna接口兼容性，但内部使用混合方案
        """
        try:
            # 使用混合方案生成查询结果
            parsed_result = self.generate_sql_with_rag_context(question, **kwargs)
            
            # 为了兼容Vanna的generate_sql接口，返回第一个SQL
            if parsed_result.queries:
                first_sql = parsed_result.queries[0].sql
                print(f"✅ [混合方案] 返回主SQL: {first_sql}")
                return first_sql
            else:
                raise ValueError("没有生成任何SQL查询")
                
        except Exception as e:
            print(f"❌ [混合方案] generate_sql失败: {e}")
            raise

    def _parse_json_response(self, json_content: str) -> DatabaseQueryResult:
        """
        解析豆包返回的JSON响应，使用与graph.py相同的解析逻辑
        """
        try:
            # 处理markdown代码块包装的JSON
            if "```json" in json_content:
                json_start = json_content.find("```json") + 7
                json_end = json_content.find("```", json_start)
                if json_end != -1:
                    json_content = json_content[json_start:json_end].strip()
                else:
                    json_content = json_content[json_start:].strip()
            elif "```" in json_content and "{" in json_content:
                lines = json_content.split('\n')
                json_lines = []
                in_code_block = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        continue
                    if in_code_block or ('{' in line or '}' in line or '"' in line):
                        json_lines.append(line)
                json_content = '\n'.join(json_lines).strip()
            else:
                # 尝试从内容中提取JSON
                json_start = json_content.find("{")
                json_end = json_content.rfind("}") + 1
                if json_start != -1 and json_end > json_start:
                    json_content = json_content[json_start:json_end]
        
            # 清理可能的尾随逗号
            json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
            
            print(f"🔧 [JSON解析] 清理后的JSON: {json_content[:200]}...")
            
            # 解析JSON
            parsed_data = json.loads(json_content)
            result = DatabaseQueryResult(**parsed_data)
            
            print(f"✅ [JSON解析] 成功解析为DatabaseQueryResult")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ [JSON解析] 失败: {e}")
            print(f"❌ [JSON解析] 原始内容: {json_content}")
            raise ValueError(f"Invalid JSON response: {json_content}")
        except Exception as e:
            print(f"❌ [JSON解析] 其他错误: {e}")
            raise

    def execute_queries_and_format(self, parsed_result: DatabaseQueryResult, question: str) -> str:
        """
        执行所有SQL查询并格式化结果，返回综合报告
        """
        query_results = []
        
        for i, sql_query in enumerate(parsed_result.queries):
            try:
                print(f"⚡ [执行SQL] 正在执行第 {i+1} 个查询: {sql_query.explanation}")
                
                # 执行数据库查询
                db_result = execute_database_query(sql_query.sql)
                
                # 格式化查询结果
                formatted_result = format_query_result(sql_query.sql, db_result)
                query_results.append(f"""
**查询 {i+1}: {sql_query.explanation}**
```sql
{sql_query.sql}
```
{formatted_result}
""")
                
            except Exception as e:
                error_result = f"""
**查询 {i+1}: {sql_query.explanation}** ❌
```sql
{sql_query.sql}
```
执行失败: {str(e)}
"""
                query_results.append(error_result)
        
        # 构建综合报告
        comprehensive_result = f"""
**Vanna智能数据库查询报告**

**原始问题:** {question}

**查询概述:** {parsed_result.summary}

{''.join(query_results)}

**总结:** 基于Vanna AI的智能分析，为您的查询需求"{question}"提供了 {len(parsed_result.queries)} 个精确的SQL查询和详细的数据分析结果。
"""
        
        return comprehensive_result

    def _create_custom_prompt(self, question: str) -> List[Dict]:
        """
        创建使用database_query_instructions的自定义提示词
        """
        # 格式化数据库schema为可读的字符串
        schema_text = self._format_database_schema()
        
        # 使用database_query_instructions模板
        system_message = database_query_instructions.format(
            database_schema=schema_text,
            current_date=get_current_date(),
            query_requirement=question
        )
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"用户查询需求: {question}"}
        ]
        
        print(f"🔧 [自定义提示词] 使用database_query_instructions生成提示词")
        
        return messages

    def _format_database_schema(self) -> str:
        """
        将数据库schema格式化为可读的字符串
        """
        schema_lines = []
        
        for table_name, table_info in DATABASE_SCHEMA.items():
            schema_lines.append(f"\n📋 表: {table_name}")
            schema_lines.append(f"   描述: {table_info['description']}")
            schema_lines.append("   字段:")
            
            for column in table_info['columns']:
                schema_lines.append(f"     • {column['name']} ({column['type']}) - {column['description']}")
        
        return '\n'.join(schema_lines)
    
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