"""
Vanna训练脚本
这个模块负责教会Vanna理解我们的数据库结构和业务逻辑
"""

from pathlib import Path
from agent.vanna_doubao import create_hr_vanna
from agent.database_schema import get_full_schema_for_ai
import json

def train_vanna_with_hr_data():
    """
    使用HR数据训练Vanna模型
    这个过程就像是给一个新员工进行入职培训，教会他我们的业务知识
    """
    
    print("🎓 开始训练Vanna模型...")
    
    # 创建Vanna实例
    vn = create_hr_vanna()
    
    # 步骤1: 训练DDL（数据库结构）
    print("📚 第一步：学习数据库结构...")
    train_ddl(vn)
    
    # 步骤2: 训练业务文档
    print("📖 第二步：学习业务知识...")
    train_documentation(vn)
    
    # 步骤3: 训练SQL样例
    print("💻 第三步：学习查询样例...")
    train_sql_examples(vn)
    
    print("🎉 Vanna训练完成！")
    return vn

def train_ddl(vn):
    """训练数据库结构信息"""
    
    # 员工基本信息表
    employee_ddl = """
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        department_id INTEGER,
        position VARCHAR(100),
        level VARCHAR(20),
        hire_date DATE,
        status VARCHAR(20) DEFAULT 'active',
        manager_id VARCHAR(20),
        email VARCHAR(100),
        salary DECIMAL(10,2),
        FOREIGN KEY (department_id) REFERENCES departments(id)
    );
    """
    vn.train(ddl=employee_ddl)
    
    # 部门信息表
    department_ddl = """
    CREATE TABLE departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        parent_id INTEGER,
        head_employee_id VARCHAR(20),
        FOREIGN KEY (parent_id) REFERENCES departments(id)
    );
    """
    vn.train(ddl=department_ddl)
    
    # 项目信息表
    project_ddl = """
    CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        status VARCHAR(50),
        start_date DATE,
        end_date DATE,
        budget DECIMAL(15,2),
        client_id INTEGER,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    );
    """
    vn.train(ddl=project_ddl)
    
    # 项目分配表
    project_assignment_ddl = """
    CREATE TABLE project_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        employee_id VARCHAR(20),
        role VARCHAR(100),
        workload_percentage DECIMAL(5,2),
        start_date DATE,
        end_date DATE,
        FOREIGN KEY (project_id) REFERENCES projects(id),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    """
    vn.train(ddl=project_assignment_ddl)
    
    # 薪资记录表
    salary_ddl = """
    CREATE TABLE salary_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id VARCHAR(20),
        month VARCHAR(7),
        base_salary DECIMAL(10,2),
        bonus DECIMAL(10,2),
        overtime_pay DECIMAL(10,2),
        deductions DECIMAL(10,2),
        total_salary DECIMAL(10,2),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );
    """
    vn.train(ddl=salary_ddl)
    
    # 客户信息表
    client_ddl = """
    CREATE TABLE clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        industry VARCHAR(100),
        contact_person VARCHAR(100),
        email VARCHAR(100),
        phone VARCHAR(50)
    );
    """
    vn.train(ddl=client_ddl)
    
    # 设备信息表
    equipment_ddl = """
    CREATE TABLE equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(200) NOT NULL,
        type VARCHAR(100),
        assigned_to VARCHAR(20),
        purchase_date DATE,
        cost DECIMAL(10,2),
        status VARCHAR(50),
        FOREIGN KEY (assigned_to) REFERENCES employees(employee_id)
    );
    """
    vn.train(ddl=equipment_ddl)

def train_documentation(vn):
    """训练业务文档和术语定义"""
    
    business_docs = [
        "员工状态说明：active表示在职员工，inactive表示已离职员工。查询时通常只关注在职员工。",
        
        "职级体系：字节跳动的职级从低到高包括：助理、专员、高级专员、主管、高级主管、经理、高级经理、总监、高级总监、VP等。",
        
        "部门架构：公司采用树形部门结构，通过parent_id字段构成上下级关系。主要部门包括技术部、产品部、设计部、运营部、市场部、人力资源部、财务部等。",
        
        "薪资构成：总薪资 = 基本工资 + 奖金 + 加班费 - 扣款。查询薪资时通常关注total_salary字段。",
        
        "项目状态：active(进行中)、completed(已完成)、cancelled(已取消)、planning(规划中)。",
        
        "时间查询约定：'今年'指当前年份，'去年'指上一年，'本月'指当前月份。日期格式统一为YYYY-MM-DD，月份格式为YYYY-MM。",
        
        "排名查询：查询'前N名'时使用ORDER BY ... DESC LIMIT N，查询'后N名'时使用ORDER BY ... ASC LIMIT N。",
        
        "设备类型：主要包括笔记本电脑、台式机、手机、平板、显示器等。设备状态包括：active(使用中)、maintenance(维修中)、retired(已报废)。"
    ]
    
    for doc in business_docs:
        vn.train(documentation=doc)

def train_sql_examples(vn):
    """训练常见的SQL查询样例"""
    
    sql_examples = [
        # 基础员工信息查询
        {
            "question": "查询所有在职员工的基本信息",
            "sql": "SELECT employee_id, name, position, d.name as department FROM employees e LEFT JOIN departments d ON e.department_id = d.id WHERE e.status = 'active'"
        },
        
        # 部门员工统计
        {
            "question": "统计各部门的员工数量",
            "sql": """
            SELECT d.name as department_name, COUNT(e.employee_id) as employee_count
            FROM departments d
            LEFT JOIN employees e ON d.id = e.department_id AND e.status = 'active'
            GROUP BY d.id, d.name
            ORDER BY employee_count DESC
            """
        },
        
        # 薪资排名查询
        {
            "question": "查询2024年度薪资最高的前10名员工",
            "sql": """
            SELECT e.name, e.position, d.name as department, AVG(s.total_salary) as avg_salary
            FROM employees e
            JOIN salary_records s ON e.employee_id = s.employee_id
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE s.month LIKE '2024-%' AND e.status = 'active'
            GROUP BY e.employee_id, e.name, e.position, d.name
            ORDER BY avg_salary DESC
            LIMIT 10
            """
        },
        
        # 项目参与情况查询
        {
            "question": "查询技术部门员工参与的项目情况",
            "sql": """
            SELECT e.name as employee_name, p.name as project_name, pa.role, pa.workload_percentage
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            JOIN project_assignments pa ON e.employee_id = pa.employee_id
            JOIN projects p ON pa.project_id = p.id
            WHERE d.name LIKE '%技术%' AND e.status = 'active'
            ORDER BY e.name, p.name
            """
        },
        
        # 薪资统计查询
        {
            "question": "统计各部门的平均薪资",
            "sql": """
            SELECT d.name as department_name, 
                   AVG(e.salary) as avg_salary,
                   COUNT(e.employee_id) as employee_count
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            WHERE e.status = 'active'
            GROUP BY d.id, d.name
            ORDER BY avg_salary DESC
            """
        },
        
        # 设备分配查询
        {
            "question": "查询员工的设备分配情况",
            "sql": """
            SELECT e.name as employee_name, 
                   eq.name as equipment_name, 
                   eq.type as equipment_type,
                   eq.status
            FROM employees e
            LEFT JOIN equipment eq ON e.employee_id = eq.assigned_to
            WHERE e.status = 'active'
            ORDER BY e.name, eq.type
            """
        }
    ]
    
    for example in sql_examples:
        vn.train(question=example["question"], sql=example["sql"])

# 训练脚本的主入口
if __name__ == "__main__":
    trained_vanna = train_vanna_with_hr_data()
    
    # 测试训练效果
    test_questions = [
        "查询技术部门薪资最高的5名员工",
        "统计各部门的员工数量",
        "查询参与项目最多的员工"
    ]
    
    for question in test_questions:
        try:
            sql = trained_vanna.generate_sql(question)
            print(f"\n测试问题: {question}")
            print(f"生成的SQL: {sql}")
        except Exception as e:
            print(f"测试失败 - {question}: {e}") 