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
    
    # 部门表（与 mysql_init.py 保持一致）
    department_ddl = """
    CREATE TABLE departments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        budget DECIMAL(12,2),
        head_id INT,
        location VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_name (name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    vn.train(ddl=department_ddl)
    
    # 员工表（与 mysql_init.py 保持一致）
    employee_ddl = """
    CREATE TABLE employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(200) UNIQUE,
        department_id INT,
        position VARCHAR(100),
        hire_date DATE,
        salary DECIMAL(10,2),
        manager_id INT,
        status VARCHAR(20) DEFAULT 'active',
        phone VARCHAR(20),
        address VARCHAR(200),
        birth_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (department_id) REFERENCES departments(id),
        FOREIGN KEY (manager_id) REFERENCES employees(id),
        INDEX idx_department (department_id),
        INDEX idx_status (status),
        INDEX idx_hire_date (hire_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    vn.train(ddl=employee_ddl)
    
    # 项目表（与 mysql_init.py 保持一致）
    project_ddl = """
    CREATE TABLE projects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        description TEXT,
        start_date DATE,
        end_date DATE,
        budget DECIMAL(12,2),
        status VARCHAR(20) DEFAULT 'planning',
        manager_id INT,
        priority VARCHAR(10),
        client VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (manager_id) REFERENCES employees(id),
        INDEX idx_status (status),
        INDEX idx_manager (manager_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    vn.train(ddl=project_ddl)
    
    # 项目分配表（与 mysql_init.py 保持一致）
    project_assignment_ddl = """
    CREATE TABLE project_assignments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        project_id INT,
        employee_id INT,
        role VARCHAR(100),
        start_date DATE,
        end_date DATE,
        workload_percentage INT,
        hourly_rate DECIMAL(8,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
        UNIQUE KEY unique_assignment (project_id, employee_id, start_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    vn.train(ddl=project_assignment_ddl)
    
    # 薪资记录表（与 mysql_init.py 保持一致）
    salary_ddl = """
    CREATE TABLE salaries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        employee_id INT,
        year INT,
        month INT,
        base_salary DECIMAL(10,2),
        bonus DECIMAL(10,2) DEFAULT 0,
        overtime_pay DECIMAL(10,2) DEFAULT 0,
        total_amount DECIMAL(10,2),
        deductions DECIMAL(8,2) DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
        UNIQUE KEY unique_salary (employee_id, year, month),
        INDEX idx_year_month (year, month)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    vn.train(ddl=salary_ddl)
    
    # 客户信息表（与 mysql_init.py 保持一致）
    client_ddl = """
    CREATE TABLE clients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        contact_person VARCHAR(100),
        email VARCHAR(200),
        phone VARCHAR(20),
        address VARCHAR(300),
        industry VARCHAR(100),
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_name (name),
        INDEX idx_status (status)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    vn.train(ddl=client_ddl)
    
    # 设备信息表（与 mysql_init.py 保持一致）
    equipment_ddl = """
    CREATE TABLE equipment (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(200) NOT NULL,
        type VARCHAR(100),
        model VARCHAR(100),
        serial_number VARCHAR(100) UNIQUE,
        purchase_date DATE,
        price DECIMAL(10,2),
        employee_id INT,
        status VARCHAR(20) DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE SET NULL,
        INDEX idx_type (type),
        INDEX idx_status (status),
        INDEX idx_employee (employee_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    vn.train(ddl=equipment_ddl)

def train_documentation(vn):
    """训练业务文档和术语定义"""
    
    business_docs = [
        "员工状态说明：active表示在职员工，inactive表示已离职员工。查询时通常只关注在职员工。",
        
        "职级体系：字节跳动的职级从低到高包括：助理、专员、高级专员、主管、高级主管、经理、高级经理、总监、高级总监、VP等。",
        
        "部门架构：公司部门信息包括部门名称、预算、负责人、所在地等。主要部门包括技术研发部、产品设计部、市场营销部、人力资源部、财务部、运营部、数据科学部、设计部等。",
        
        "薪资数据结构：薪资信息存储在salaries表中，包含以下字段：employee_id(员工ID)、year(年份)、month(月份)、base_salary(基本工资)、bonus(奖金)、overtime_pay(加班费)、total_amount(总薪资)、deductions(扣款)、created_at(创建时间)。查询薪资时主要关注total_amount字段。",
        
        "薪资查询规则：查询年度薪资时，使用salaries表并按year和month进行筛选。计算平均薪资时使用AVG(total_amount)，计算总薪资时使用SUM(total_amount)。",
        
        "项目状态：active(进行中)、completed(已完成)、cancelled(已取消)、planning(规划中)。",
        
        "时间查询约定：'今年'指当前年份，'去年'指上一年，'本月'指当前月份。查询年份时使用YEAR()函数，查询月份时使用MONTH()函数。",
        
        "表结构映射：员工表(employees)、部门表(departments)、薪资表(salaries)、项目表(projects)、项目分配表(project_assignments)、客户表(clients)、设备表(equipment)。",
        
        "常用字段映射：员工薪资使用employees.salary字段（基本薪资）或salaries.total_amount字段（详细薪资记录）；员工部门通过employees.department_id关联departments.id；日期字段统一使用MySQL的DATE和TIMESTAMP类型。",
        
        "排名查询：查询'前N名'时使用ORDER BY ... DESC LIMIT N，查询'后N名'时使用ORDER BY ... ASC LIMIT N。",
        
        "设备管理：设备类型包括笔记本电脑、台式机、手机、平板、显示器等。设备状态包括：active(使用中)、maintenance(维修中)、retired(已报废)。",
        
        "客户管理：客户状态包括：active(活跃)、inactive(非活跃)、potential(潜在客户)。客户信息包含联系人、行业等详细信息。"
    ]
    
    for doc in business_docs:
        vn.train(documentation=doc)

def train_sql_examples(vn):
    """训练常见的SQL查询样例"""
    
    sql_examples = [
        # 基础员工信息查询
        {
            "question": "查询所有在职员工的基本信息",
            "sql": "SELECT id, name, position, d.name as department FROM employees e LEFT JOIN departments d ON e.department_id = d.id WHERE e.status = 'active'"
        },
        
        # 部门员工统计
        {
            "question": "统计各部门的员工数量",
            "sql": """
            SELECT d.name as department_name, COUNT(e.id) as employee_count
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
            SELECT e.name, e.position, d.name as department, AVG(s.total_amount) as avg_salary
            FROM employees e
            JOIN salaries s ON e.id = s.employee_id
            LEFT JOIN departments d ON e.department_id = d.id
            WHERE s.year = 2024 AND e.status = 'active'
            GROUP BY e.id, e.name, e.position, d.name
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
            JOIN project_assignments pa ON e.id = pa.employee_id
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
                   COUNT(e.id) as employee_count
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
                   eq.model,
                   eq.status
            FROM employees e
            LEFT JOIN equipment eq ON e.id = eq.employee_id
            WHERE e.status = 'active'
            ORDER BY e.name, eq.type
            """
        },
        
        # 客户信息查询
        {
            "question": "查询活跃客户信息",
            "sql": """
            SELECT name as client_name,
                   contact_person,
                   email,
                   phone,
                   industry
            FROM clients
            WHERE status = 'active'
            ORDER BY name
            """
        },
        
        # 薪资统计样例 - 2024年薪资查询
        {
            "question": "查询2024年所有员工的总薪资",
            "sql": """
            SELECT SUM(total_amount) as total_salary_2024
            FROM salaries
            WHERE year = 2024
            """
        },
        
        # 薪资统计样例 - 2024年平均薪资
        {
            "question": "查询2024年员工的平均薪资",
            "sql": """
            SELECT AVG(total_amount) as average_salary
            FROM salaries
            WHERE year = 2024
            """
        },
        
        # 薪资统计样例 - 按部门统计2024年薪资
        {
            "question": "查询2024年各部门的平均薪资",
            "sql": """
            SELECT d.name as department_name, AVG(s.total_amount) as average_salary
            FROM salaries s
            JOIN employees e ON s.employee_id = e.id
            JOIN departments d ON e.department_id = d.id
            WHERE s.year = 2024 AND e.status = 'active'
            GROUP BY d.id, d.name
            ORDER BY average_salary DESC
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