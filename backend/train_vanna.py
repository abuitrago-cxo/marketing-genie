#!/usr/bin/env python3
"""
Vanna训练脚本 - 使用正确的数据库schema
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

def train_vanna_with_correct_schema():
    """使用正确的schema训练Vanna"""
    try:
        print("🚀 开始训练Vanna...")
        
        # 创建Vanna实例
        vn = create_hr_vanna()
        
        # 训练正确的DDL - employees表
        employees_ddl = """
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(200) UNIQUE NOT NULL,
            department_id INTEGER,
            position VARCHAR(100),
            hire_date DATE,
            salary DECIMAL(10,2),
            status VARCHAR(20) DEFAULT 'active',
            FOREIGN KEY (department_id) REFERENCES departments(id)
        );
        """
        vn.train(ddl=employees_ddl)
        print("✅ employees表DDL训练完成")
        
        # 训练departments表
        departments_ddl = """
        CREATE TABLE departments (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            budget DECIMAL(12,2),
            head_id INTEGER,
            location VARCHAR(100),
            FOREIGN KEY (head_id) REFERENCES employees(id)
        );
        """
        vn.train(ddl=departments_ddl)
        print("✅ departments表DDL训练完成")
        
        # 训练projects表
        projects_ddl = """
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            start_date DATE,
            end_date DATE,
            budget DECIMAL(12,2),
            manager_id INTEGER,
            status VARCHAR(50) DEFAULT 'active',
            FOREIGN KEY (manager_id) REFERENCES employees(id)
        );
        """
        vn.train(ddl=projects_ddl)
        print("✅ projects表DDL训练完成")
        
        # 训练客户信息表
        customers_ddl = """
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name VARCHAR(200) NOT NULL,
            contact_email VARCHAR(200),
            contact_phone VARCHAR(50),
            industry VARCHAR(100)
        );
        """
        vn.train(ddl=customers_ddl)
        print("✅ customers表DDL训练完成")
        
        # 添加一些示例查询训练
        example_queries = [
            {
                "question": "查询所有员工的姓名和薪资",
                "sql": "SELECT name, salary FROM employees;"
            },
            {
                "question": "查询2024年入职的员工数量",
                "sql": "SELECT COUNT(*) FROM employees WHERE YEAR(hire_date) = 2024;"
            },
            {
                "question": "查询每个部门的员工总数",
                "sql": "SELECT d.name, COUNT(e.id) as employee_count FROM departments d LEFT JOIN employees e ON d.id = e.department_id GROUP BY d.id, d.name;"
            },
            {
                "question": "查询薪资最高的前10名员工",
                "sql": "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 10;"
            },
            {
                "question": "查询在职员工的平均薪资",
                "sql": "SELECT AVG(salary) FROM employees WHERE status = 'active';"
            },
            {
                "question": "查询所有部门的总预算",
                "sql": "SELECT SUM(budget) FROM departments;"
            }
        ]
        
        for example in example_queries:
            vn.train(question=example["question"], sql=example["sql"])
            print(f"✅ 训练查询: {example['question']}")
        
        # 测试训练效果
        print("\n🧪 测试训练效果...")
        test_questions = [
            "查询所有员工的姓名",
            "2024年发放了多少薪资",
            "每个部门有多少员工"
        ]
        
        for question in test_questions:
            try:
                sql = vn.generate_sql(question)
                print(f"✅ 问题: {question}")
                print(f"   SQL: {sql}\n")
            except Exception as e:
                print(f"❌ 问题: {question}")
                print(f"   错误: {e}\n")
        
        print("🎉 Vanna训练完成！")
        return True
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if train_vanna_with_correct_schema():
        print("✅ 训练成功完成")
    else:
        print("❌ 训练失败")
        sys.exit(1) 