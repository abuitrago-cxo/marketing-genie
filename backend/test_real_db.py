#!/usr/bin/env python3
"""
独立的数据库测试脚本
测试真实SQLite数据库的连接和查询功能
"""

import sqlite3
from pathlib import Path

# 数据库文件路径
DATABASE_PATH = Path(__file__).parent / "data" / "company.db"

def get_database_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_database_query(sql: str):
    """执行数据库查询"""
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        print(f"🔍 [数据库查询] 执行SQL: {sql}")
        
        cursor.execute(sql)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            row_dict = {}
            for i, column in enumerate(columns):
                row_dict[column] = row[i]
            data.append(row_dict)
        
        conn.close()
        
        print(f"✅ [查询成功] 返回 {len(data)} 行数据")
        return {
            "success": True,
            "data": data,
            "row_count": len(data),
            "columns": columns
        }
        
    except Exception as e:
        print(f"❌ [查询错误] {e}")
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "row_count": 0
        }

def format_result_table(result):
    """格式化结果为表格"""
    if not result["success"]:
        return f"错误: {result['error']}"
    
    data = result["data"]
    columns = result["columns"]
    
    if not data:
        return "无数据"
    
    # 计算列宽
    col_widths = {}
    for col in columns:
        col_widths[col] = len(col)
        for row in data:
            value = str(row.get(col, ""))
            col_widths[col] = max(col_widths[col], len(value))
    
    # 构建表格
    table = ""
    
    # 表头
    header = "| " + " | ".join(col.ljust(col_widths[col]) for col in columns) + " |"
    table += header + "\n"
    
    # 分隔符
    separator = "|" + "|".join("-" * (col_widths[col] + 2) for col in columns) + "|"
    table += separator + "\n"
    
    # 数据行
    for row in data[:10]:  # 限制显示前10行
        row_str = "| " + " | ".join(str(row.get(col, "")).ljust(col_widths[col]) for col in columns) + " |"
        table += row_str + "\n"
    
    if len(data) > 10:
        table += f"...(共{len(data)}行，仅显示前10行)\n"
    
    return table

def main():
    """主测试函数"""
    print("🚀 开始测试真实数据库...")
    
    # 检查数据库文件
    if not DATABASE_PATH.exists():
        print(f"❌ 数据库文件不存在: {DATABASE_PATH}")
        return
    
    print(f"✅ 数据库文件存在: {DATABASE_PATH}")
    
    # 测试查询
    test_queries = [
        "SELECT COUNT(*) as total_employees FROM employees",
        "SELECT name, position, salary FROM employees LIMIT 5",
        "SELECT d.name as department, COUNT(e.id) as employee_count FROM departments d LEFT JOIN employees e ON d.id = e.department_id GROUP BY d.name",
        "SELECT p.name, p.status, p.budget FROM projects p WHERE p.status = 'active'",
        "SELECT e.name, d.name as department, e.salary FROM employees e JOIN departments d ON e.department_id = d.id WHERE e.salary > 25000 ORDER BY e.salary DESC"
    ]
    
    for i, sql in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}: {sql}")
        print('='*80)
        
        result = execute_database_query(sql)
        table = format_result_table(result)
        print(table)

if __name__ == "__main__":
    main() 