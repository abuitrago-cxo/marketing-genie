import sqlite3
import os
import random
from pathlib import Path
from datetime import datetime, timedelta

# 延迟导入Faker，只在需要时导入
try:
    from faker import Faker
    fake = Faker(['zh_CN', 'en_US'])
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    fake = None

# 数据库文件路径
DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "company.db"

def init_database():
    """初始化数据库，创建表结构并插入大量随机数据"""
    # 确保数据目录存在
    DATABASE_PATH.parent.mkdir(exist_ok=True)
    
    # 连接数据库（如果不存在会自动创建）
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # 创建部门表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                budget DECIMAL(12,2),
                head_id INTEGER,
                location VARCHAR(100)
            )
        ''')
        
        # 创建员工表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(200) UNIQUE,
                department_id INTEGER,
                position VARCHAR(100),
                hire_date DATE,
                salary DECIMAL(10,2),
                manager_id INTEGER,
                status VARCHAR(20) DEFAULT 'active',
                phone VARCHAR(20),
                address VARCHAR(200),
                birth_date DATE,
                FOREIGN KEY (department_id) REFERENCES departments(id),
                FOREIGN KEY (manager_id) REFERENCES employees(id)
            )
        ''')
        
        # 创建项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                description TEXT,
                start_date DATE,
                end_date DATE,
                budget DECIMAL(12,2),
                status VARCHAR(20) DEFAULT 'planning',
                manager_id INTEGER,
                priority VARCHAR(10),
                client VARCHAR(100),
                FOREIGN KEY (manager_id) REFERENCES employees(id)
            )
        ''')
        
        # 创建项目分配表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                employee_id INTEGER,
                role VARCHAR(100),
                start_date DATE,
                end_date DATE,
                workload_percentage INTEGER,
                hourly_rate DECIMAL(8,2),
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        ''')
        
        # 创建薪资记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                year INTEGER,
                month INTEGER,
                base_salary DECIMAL(10,2),
                bonus DECIMAL(10,2) DEFAULT 0,
                overtime_pay DECIMAL(10,2) DEFAULT 0,
                total_amount DECIMAL(10,2),
                deductions DECIMAL(8,2) DEFAULT 0,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        ''')
        
        # 创建客户表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                contact_person VARCHAR(100),
                email VARCHAR(200),
                phone VARCHAR(20),
                address VARCHAR(300),
                industry VARCHAR(100),
                status VARCHAR(20) DEFAULT 'active'
            )
        ''')
        
        # 创建设备表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                type VARCHAR(100),
                model VARCHAR(100),
                serial_number VARCHAR(100) UNIQUE,
                purchase_date DATE,
                price DECIMAL(10,2),
                employee_id INTEGER,
                status VARCHAR(20) DEFAULT 'active',
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        ''')
        
        # 检查是否已有数据，如果没有则插入大量随机数据
        cursor.execute("SELECT COUNT(*) FROM departments")
        if cursor.fetchone()[0] == 0:
            if FAKER_AVAILABLE:
                insert_large_sample_data(cursor)
            else:
                print("⚠️ Faker库未安装，跳过数据生成。数据库已存在则正常使用。")
        
        # 更新部门表的head_id外键约束
        cursor.execute('''
            UPDATE departments 
            SET head_id = (
                SELECT id FROM employees 
                WHERE employees.department_id = departments.id 
                AND (employees.position LIKE '%总监%' OR employees.position LIKE '%经理%' OR employees.position LIKE '%主管%')
                LIMIT 1
            )
        ''')
        
        conn.commit()
        print("✅ 数据库初始化成功！")
        
        # 显示数据统计
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM employees")
        emp_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM projects")
        proj_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]
        
        print(f"📊 数据统计: {dept_count}个部门, {emp_count}名员工, {proj_count}个项目, {client_count}个客户")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        conn.close()

def insert_large_sample_data(cursor):
    """插入大量随机示例数据"""
    if not FAKER_AVAILABLE:
        print("❌ Faker库未安装，无法生成随机数据")
        return
    
    # 定义部门和职位数据
    departments_data = [
        ('技术部', 8000000.00, '北京'),
        ('产品部', 3000000.00, '北京'),
        ('设计部', 2500000.00, '上海'),
        ('市场部', 4000000.00, '深圳'),
        ('销售部', 5000000.00, '广州'),
        ('人事部', 1500000.00, '北京'),
        ('财务部', 2000000.00, '北京'),
        ('运营部', 3500000.00, '成都'),
        ('客服部', 1800000.00, '杭州'),
        ('法务部', 1200000.00, '北京'),
        ('行政部', 1000000.00, '北京'),
        ('研发部', 10000000.00, '深圳'),
        ('质量部', 1500000.00, '苏州'),
        ('采购部', 2200000.00, '上海'),
        ('物流部', 2800000.00, '广州')
    ]
    
    positions_by_dept = {
        '技术部': ['高级工程师', '前端工程师', '后端工程师', '全栈工程师', '技术总监', '架构师', 'DevOps工程师', '测试工程师'],
        '产品部': ['产品经理', '高级产品经理', '产品总监', '产品助理', '产品运营', '需求分析师'],
        '设计部': ['UI设计师', 'UX设计师', '视觉设计师', '交互设计师', '设计总监', '平面设计师'],
        '市场部': ['市场经理', '市场总监', '品牌经理', '市场专员', '营销策划', '市场分析师'],
        '销售部': ['销售经理', '销售总监', '客户经理', '销售代表', '渠道经理', '销售助理'],
        '人事部': ['HR经理', 'HR总监', '招聘专员', '薪酬专员', '培训师', 'HRBP'],
        '财务部': ['财务经理', '财务总监', '会计师', '出纳', '税务专员', '财务分析师'],
        '运营部': ['运营经理', '运营总监', '数据分析师', '运营专员', '内容运营', '用户运营'],
        '客服部': ['客服经理', '客服主管', '客服专员', '技术支持', '售后服务专员'],
        '法务部': ['法务经理', '法务专员', '合规专员', '知识产权专员'],
        '行政部': ['行政经理', '行政助理', '前台', '司机', '保安'],
        '研发部': ['研发总监', '高级研发工程师', '算法工程师', '数据科学家', 'AI工程师', '机器学习工程师'],
        '质量部': ['质量经理', '质量工程师', 'QA工程师', '测试主管'],
        '采购部': ['采购经理', '采购专员', '供应商管理', '成本分析师'],
        '物流部': ['物流经理', '仓储主管', '配送专员', '物流协调员']
    }
    
    cities = ['北京', '上海', '深圳', '广州', '杭州', '成都', '南京', '武汉', '西安', '苏州']
    
    # 插入部门数据
    print("🏢 插入部门数据...")
    dept_list = []
    for name, budget, location in departments_data:
        dept_list.append((name, budget, None, location))
    
    cursor.executemany(
        "INSERT INTO departments (name, budget, head_id, location) VALUES (?, ?, ?, ?)",
        dept_list
    )
    
    # 获取部门ID映射
    cursor.execute("SELECT id, name FROM departments")
    dept_map = {name: id for id, name in cursor.fetchall()}
    
    # 插入大量员工数据 (300名员工)
    print("👥 插入300名员工数据...")
    employees = []
    
    for i in range(300):
        name = fake.name()
        email = f"{fake.user_name()}{i}@{fake.domain_name()}"  # 确保邮箱唯一
        
        # 随机选择部门
        dept_name = random.choice(list(dept_map.keys()))
        dept_id = dept_map[dept_name]
        
        # 根据部门选择职位
        position = random.choice(positions_by_dept[dept_name])
        
        # 根据职位确定薪资范围
        salary_ranges = {
            '助理': (8000, 15000),
            '专员': (12000, 20000),
            '工程师': (15000, 35000),
            '高级': (25000, 50000),
            '经理': (30000, 60000),
            '主管': (25000, 45000),
            '总监': (50000, 100000),
            '架构师': (40000, 80000)
        }
        
        salary_range = (15000, 30000)  # 默认范围
        for key, range_val in salary_ranges.items():
            if key in position:
                salary_range = range_val
                break
        
        salary = random.randint(salary_range[0], salary_range[1])
        hire_date = fake.date_between(start_date='-5y', end_date='today')
        phone = fake.phone_number()
        address = fake.address()
        birth_date = fake.date_between(start_date='-50y', end_date='-22y')
        
        employees.append((
            name, email, dept_id, position, hire_date, salary, 
            None, 'active', phone, address, birth_date
        ))
    
    cursor.executemany(
        """INSERT INTO employees (name, email, department_id, position, hire_date, salary, 
           manager_id, status, phone, address, birth_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        employees
    )
    
    # 设置管理层关系
    print("👔 设置管理层关系...")
    cursor.execute("""
        UPDATE employees SET manager_id = (
            SELECT e2.id FROM employees e2 
            WHERE e2.department_id = employees.department_id 
            AND (e2.position LIKE '%总监%' OR e2.position LIKE '%经理%')
            AND e2.id != employees.id
            LIMIT 1
        ) WHERE position NOT LIKE '%总监%' AND position NOT LIKE '%经理%'
    """)
    
    # 插入客户数据 (50个客户)
    print("🏢 插入50个客户数据...")
    clients = []
    industries = ['互联网', '金融', '教育', '医疗', '零售', '制造业', '房地产', '物流', '娱乐', '政府']
    
    for i in range(50):
        clients.append((
            fake.company(),
            fake.name(),
            f"{fake.user_name()}_client{i}@{fake.domain_name()}",
            fake.phone_number(),
            fake.address(),
            random.choice(industries),
            random.choice(['active', 'inactive', 'potential'])
        ))
    
    cursor.executemany(
        "INSERT INTO clients (name, contact_person, email, phone, address, industry, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        clients
    )
    
    # 获取客户ID
    cursor.execute("SELECT id FROM clients")
    client_ids = [row[0] for row in cursor.fetchall()]
    
    # 插入项目数据 (80个项目)
    print("📋 插入80个项目数据...")
    projects = []
    project_types = ['网站开发', '移动应用', '系统集成', '数据分析', 'AI项目', '电商平台', '管理系统', '微服务架构']
    statuses = ['planning', 'active', 'completed', 'on_hold', 'cancelled']
    priorities = ['high', 'medium', 'low']
    
    # 获取可以做项目经理的员工ID
    cursor.execute("SELECT id FROM employees WHERE position LIKE '%经理%' OR position LIKE '%总监%'")
    manager_ids = [row[0] for row in cursor.fetchall()]
    
    for i in range(80):
        project_type = random.choice(project_types)
        start_date = fake.date_between(start_date='-2y', end_date='+6m')
        end_date = start_date + timedelta(days=random.randint(30, 365))
        
        projects.append((
            f"{fake.company()}{project_type}",
            fake.text(max_nb_chars=200),
            start_date,
            end_date,
            random.randint(100000, 5000000),
            random.choice(statuses),
            random.choice(manager_ids) if manager_ids else None,
            random.choice(priorities),
            random.choice(client_ids) if client_ids else None
        ))
    
    cursor.executemany(
        """INSERT INTO projects (name, description, start_date, end_date, budget, status, 
           manager_id, priority, client) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        projects
    )
    
    # 获取项目ID和员工ID
    cursor.execute("SELECT id FROM projects")
    project_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT id FROM employees")
    employee_ids = [row[0] for row in cursor.fetchall()]
    
    # 插入项目分配数据 (每个项目分配2-6个员工)
    print("📝 插入项目分配数据...")
    assignments = []
    roles = ['开发工程师', '前端开发', '后端开发', '测试工程师', '产品经理', '设计师', '项目助理']
    
    for project_id in project_ids:
        # 每个项目分配2-6个员工
        num_assignments = random.randint(2, 6)
        assigned_employees = random.sample(employee_ids, min(num_assignments, len(employee_ids)))
        
        for emp_id in assigned_employees:
            start_date = fake.date_between(start_date='-1y', end_date='today')
            end_date = start_date + timedelta(days=random.randint(30, 180))
            
            assignments.append((
                project_id,
                emp_id,
                random.choice(roles),
                start_date,
                end_date,
                random.randint(20, 100),
                random.randint(200, 800)
            ))
    
    cursor.executemany(
        """INSERT INTO project_assignments (project_id, employee_id, role, start_date, 
           end_date, workload_percentage, hourly_rate) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        assignments
    )
    
    # 插入薪资记录数据 (最近12个月)
    print("💰 插入薪资记录数据...")
    salaries = []
    
    # 获取所有员工的基本薪资
    cursor.execute("SELECT id, salary FROM employees")
    employee_salaries = cursor.fetchall()
    
    # 生成最近12个月的薪资数据
    for emp_id, base_salary in employee_salaries:
        for month_offset in range(12):
            date = datetime.now() - timedelta(days=30 * month_offset)
            year = date.year
            month = date.month
            
            # 随机波动±5%
            monthly_salary = base_salary * random.uniform(0.95, 1.05)
            bonus = random.randint(0, 10000) if month in [6, 12] else random.randint(0, 2000)
            overtime = random.randint(0, 3000)
            deductions = random.randint(500, 2000)
            total = monthly_salary + bonus + overtime - deductions
            
            salaries.append((emp_id, year, month, monthly_salary, bonus, overtime, total, deductions))
    
    cursor.executemany(
        """INSERT INTO salaries (employee_id, year, month, base_salary, bonus, overtime_pay, 
           total_amount, deductions) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        salaries
    )
    
    # 插入设备数据
    print("💻 插入设备数据...")
    equipment = []
    equipment_types = ['笔记本电脑', '台式机', '显示器', '手机', '平板', '打印机', '投影仪', '路由器']
    brands = ['苹果', '戴尔', '联想', '华为', '小米', '惠普', '华硕', '三星']
    
    for i in range(150):
        equipment.append((
            f"{random.choice(brands)} {random.choice(equipment_types)}",
            random.choice(equipment_types),
            fake.word(),
            fake.uuid4()[:20],
            fake.date_between(start_date='-3y', end_date='today'),
            random.randint(1000, 20000),
            random.choice(employee_ids),
            random.choice(['active', 'maintenance', 'retired'])
        ))
    
    cursor.executemany(
        """INSERT INTO equipment (name, type, model, serial_number, purchase_date, 
           price, employee_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        equipment
    )
    
    print(f"✅ 成功插入大量随机数据!")
    print(f"   - {len(departments_data)}个部门")
    print(f"   - 300名员工")
    print(f"   - 50个客户")
    print(f"   - 80个项目")
    print(f"   - {len(assignments)}个项目分配")
    print(f"   - {len(salaries)}条薪资记录")
    print(f"   - 150台设备")

def get_database_connection():
    """获取数据库连接"""
    if not DATABASE_PATH.exists():
        print("⚠️ 数据库不存在，正在初始化...")
        init_database()
    
    conn = sqlite3.connect(DATABASE_PATH)
    # 设置Row factory以便返回字典格式的结果
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    # 先删除现有数据库，重新生成
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
        print("🗑️ 删除现有数据库文件")
    
    init_database() 