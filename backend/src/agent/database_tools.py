import mysql.connector
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import os

class SQLQuery(BaseModel):
    """单个SQL查询及其结果"""
    sql: str = Field(description="生成的SQL查询语句")
    explanation: str = Field(description="对该SQL查询的解释说明")
    result_description: str = Field(description="预期结果的描述")

class DatabaseQueryResult(BaseModel):
    """数据库查询结果"""
    queries: List[SQLQuery] = Field(description="生成的SQL查询列表")
    summary: str = Field(description="查询结果的总结说明")

def get_mysql_connection():
    """获取MySQL数据库连接"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'bytedance_hr'),
            charset='utf8mb4',
            autocommit=True
        )
        return conn
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        raise

def execute_database_query(sql: str) -> Dict[str, Any]:
    """
    执行MySQL数据库查询
    """
    # 安全检查：只允许SELECT查询
    sql_lower = sql.lower().strip()
    
    # 检查是否包含危险操作
    dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'create', 'truncate']
    if any(keyword in sql_lower for keyword in dangerous_keywords):
        return {
            "success": False,
            "error": "查询包含不被允许的操作",
            "data": [],
            "row_count": 0
        }
    
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)  # MySQL返回字典格式
        
        print(f"🔍 [数据库查询] 执行SQL (MySQL): {sql}")
        
        # 执行查询
        cursor.execute(sql)
        
        # MySQL处理
        rows = cursor.fetchall()
        columns = list(rows[0].keys()) if rows else []
        data = rows
        
        conn.close()
        
        result = {
            "success": True,
            "data": data,
            "row_count": len(data),
            "columns": columns
        }
        
        print(f"✅ [查询成功] 返回 {len(data)} 行数据")
        return result
        
    except mysql.connector.Error as e:
        print(f"❌ [数据库错误] {e}")
        return {
            "success": False,
            "error": f"数据库查询错误: {str(e)}",
            "data": [],
            "row_count": 0
        }
    except Exception as e:
        print(f"❌ [系统错误] {e}")
        return {
            "success": False,
            "error": f"系统错误: {str(e)}",
            "data": [],
            "row_count": 0
        }

def format_query_result(sql: str, result: Dict[str, Any]) -> str:
    """
    格式化SQL查询结果为文本展示
    """
    if not result["success"]:
        return f"""
            **SQL查询:**
            ```sql
            {sql}
            ```

            **错误:** {result.get('error', '查询失败')}
        """
    
    data = result["data"]
    columns = result["columns"]
    row_count = result["row_count"]
    
    # 构建表格
    table_text = ""
    if data and columns:
        # 表头
        table_text += "| " + " | ".join(columns) + " |\n"
        table_text += "|" + "|".join([" --- " for _ in columns]) + "|\n"
        
        # 数据行（最多显示20行）
        display_limit = 20
        for row in data[:display_limit]:
            formatted_row = []
            for col in columns:
                value = row.get(col, "")
                # 处理None值和格式化数字
                if value is None:
                    formatted_value = "NULL"
                elif isinstance(value, float):
                    # 格式化浮点数，保留2位小数
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                formatted_row.append(formatted_value)
            table_text += "| " + " | ".join(formatted_row) + " |\n"
        
        if len(data) > display_limit:
            table_text += f"...(共{row_count}行，仅显示前{display_limit}行)\n"
    
    return f"""
        **SQL查询:**
        ```sql
        {sql}
        ```

        **查询结果:** ({row_count}行)
        {table_text if table_text else "无数据"}
    """

def test_database_connection():
    """测试数据库连接和基本查询"""
    try:
        result = execute_database_query("SELECT COUNT(*) as total_employees FROM employees")
        if result["success"]:
            total = result["data"][0]["total_employees"]
            print(f"✅ 数据库连接测试成功！当前员工总数: {total}")
            return True
        else:
            print(f"❌ 数据库查询失败: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

if __name__ == "__main__":
    # 测试数据库连接
    print("🔍 测试数据库连接...")
    test_database_connection()
    
    # 测试一些示例查询
    test_queries = [
        "SELECT name, position, salary FROM employees LIMIT 5",
        "SELECT d.name as department, COUNT(e.id) as employee_count FROM departments d LEFT JOIN employees e ON d.id = e.department_id GROUP BY d.name",
        "SELECT p.name, p.status, p.budget FROM projects p WHERE p.status = 'active'"
    ]
    
    for sql in test_queries:
        print(f"\n{'='*60}")
        print(f"测试查询: {sql}")
        result = execute_database_query(sql)
        formatted = format_query_result(sql, result)
        print(formatted) 