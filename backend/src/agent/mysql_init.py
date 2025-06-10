import mysql.connector
import os
import random
from datetime import datetime, timedelta

# 延迟导入Faker，只在需要时导入
try:
    from faker import Faker
    fake = Faker(['zh_CN', 'en_US'])
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False
    fake = None

def get_mysql_connection():
    """获取MySQL数据库连接"""
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'bytedance_hr'),
        charset='utf8mb4',
        autocommit=True
    )

def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    try:
        # 连接到MySQL服务器（不指定数据库）
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', '3306')),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        database_name = os.getenv('MYSQL_DATABASE', 'bytedance_hr')
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ 数据库 {database_name} 已创建或已存在")
        
        conn.close()
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        raise

def init_mysql_database():
    """初始化MySQL数据库，创建表结构并插入数据"""
    
    # 确保数据库存在
    create_database_if_not_exists()
    
    # 连接到具体数据库
    conn = get_mysql_connection()
    cursor = conn.cursor()
    
    try:
        # 创建部门表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                budget DECIMAL(12,2),
                head_id INT,
                location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建员工表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建项目分配表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_assignments (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建薪资记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS salaries (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建客户信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        # 创建设备信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        ''')
        
        print("✅ MySQL表结构创建完成")
        
        # 检查是否已有完整数据（以员工表为准，因为它是核心数据）
        cursor.execute("SELECT COUNT(*) FROM employees")
        emp_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM departments")
        dept_count = cursor.fetchone()[0]
        
        if emp_count == 0:
            print("📊 开始生成示例数据...")
            insert_sample_data(cursor)
        else:
            print(f"📊 数据库已包含完整数据: {dept_count} 个部门, {emp_count} 个员工")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ MySQL数据库初始化失败: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def insert_sample_data(cursor):
    """插入示例数据"""
    if not FAKER_AVAILABLE:
        print("⚠️ Faker库未安装，跳过生成示例数据")
        return
    
    # 插入部门数据
    departments = [
        ('技术研发部', 5000000.00, None, '北京'),
        ('产品设计部', 3000000.00, None, '上海'),
        ('市场营销部', 2000000.00, None, '广州'),
        ('人力资源部', 1500000.00, None, '深圳'),
        ('财务部', 1000000.00, None, '北京'),
        ('运营部', 2500000.00, None, '杭州'),
        ('数据科学部', 4000000.00, None, '北京'),
        ('设计部', 1800000.00, None, '上海')
    ]
    
    cursor.executemany(
        "INSERT INTO departments (name, budget, head_id, location) VALUES (%s, %s, %s, %s)",
        departments
    )
    print(f"✅ 已插入 {len(departments)} 个部门")
    
    # 插入员工数据
    positions_by_dept = {
        1: ['高级工程师', '资深工程师', '技术专家', '架构师', '研发经理'],
        2: ['产品经理', '高级产品经理', '产品总监', '交互设计师', '产品运营'],
        3: ['市场专员', '营销经理', '品牌经理', '市场总监', '商务经理'],
        4: ['HR专员', 'HR经理', 'HRBP', '招聘经理', '培训师'],
        5: ['会计', '财务分析师', '财务经理', '审计专员', '成本分析师'],
        6: ['运营专员', '运营经理', '数据运营', '用户运营', '内容运营'],
        7: ['数据分析师', '算法工程师', '机器学习工程师', '数据科学家', '大数据工程师'],
        8: ['UI设计师', 'UX设计师', '视觉设计师', '动效设计师', '设计总监']
    }
    
    employees = []
    for dept_id in range(1, 9):
        positions = positions_by_dept[dept_id]
        # 每个部门15-25个员工
        for _ in range(random.randint(15, 25)):
            name = fake.name()
            email = f"{fake.user_name()}@bytedance.com"
            position = random.choice(positions)
            hire_date = fake.date_between(start_date='-3y', end_date='today')
            salary = random.randint(15000, 80000)
            manager_id = None  # 暂时不设置经理
            status = random.choices(['active', 'inactive'], weights=[95, 5])[0]
            phone = fake.phone_number()[:15]  # 限制电话号码长度
            address = fake.address()
            birth_date = fake.date_of_birth(minimum_age=22, maximum_age=50)
            
            employees.append((
                name, email, dept_id, position, hire_date, salary, 
                manager_id, status, phone, address, birth_date
            ))
    
    try:
        cursor.executemany("""
            INSERT INTO employees (name, email, department_id, position, hire_date, 
                                 salary, manager_id, status, phone, address, birth_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, employees)
        print(f"✅ 已插入 {len(employees)} 个员工")
    except mysql.connector.Error as e:
        print(f"⚠️ 插入员工数据时出现重复，已跳过: {e}")
    
    # 生成项目数据
    projects = []
    for i in range(20):
        name = f"项目{fake.word().title()}{i+1}"
        description = fake.text(max_nb_chars=200)
        start_date = fake.date_between(start_date='-1y', end_date='today')
        end_date = fake.date_between(start_date=start_date, end_date='+6m')
        budget = random.randint(100000, 5000000)
        status = random.choice(['planning', 'active', 'completed', 'on_hold'])
        priority = random.choice(['low', 'medium', 'high'])
        client = fake.company()
        
        projects.append((
            name, description, start_date, end_date, budget, 
            status, None, priority, client
        ))
    
    cursor.executemany("""
        INSERT INTO projects (name, description, start_date, end_date, budget, 
                            status, manager_id, priority, client)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, projects)
    print(f"✅ 已插入 {len(projects)} 个项目")
    
    # 生成客户数据
    clients = []
    for i in range(15):
        name = fake.company()
        contact_person = fake.name()
        email = fake.email()
        phone = fake.phone_number()
        address = fake.address()
        industry = random.choice(['科技', '金融', '教育', '医疗', '制造业', '零售', '房地产', '媒体'])
        status = random.choices(['active', 'inactive', 'potential'], weights=[70, 20, 10])[0]
        
        clients.append((name, contact_person, email, phone, address, industry, status))
    
    cursor.executemany("""
        INSERT INTO clients (name, contact_person, email, phone, address, industry, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, clients)
    print(f"✅ 已插入 {len(clients)} 个客户")
    
    # 生成设备数据
    equipment_types = ['笔记本电脑', '台式机', '显示器', '手机', '平板', '投影仪', '打印机']
    equipment_list = []
    
    # 随机为部分员工分配设备
    cursor.execute("SELECT id FROM employees WHERE status = 'active' LIMIT 50")
    active_employees = [row[0] for row in cursor.fetchall()]
    
    # 如果没有活跃员工，跳过设备分配
    if not active_employees:
        print("⚠️ 没有活跃员工，跳过设备分配")
        return
    
    for i in range(80):
        eq_type = random.choice(equipment_types)
        name = f"{eq_type}-{fake.random_number(digits=4, fix_len=True)}"
        model = f"Model-{fake.random_number(digits=3, fix_len=True)}"
        serial_number = fake.uuid4()[:12].upper()
        purchase_date = fake.date_between(start_date='-2y', end_date='today')
        price = random.randint(1000, 15000)
        employee_id = random.choice(active_employees) if random.random() > 0.3 else None  # 70%分配给员工
        status = random.choices(['active', 'maintenance', 'retired'], weights=[80, 15, 5])[0]
        
        equipment_list.append((name, eq_type, model, serial_number, purchase_date, price, employee_id, status))
    
    cursor.executemany("""
        INSERT INTO equipment (name, type, model, serial_number, purchase_date, price, employee_id, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, equipment_list)
    print(f"✅ 已插入 {len(equipment_list)} 个设备")
    
    # 生成薪资数据（为所有活跃员工生成最近12个月的薪资记录）
    cursor.execute("SELECT id, salary FROM employees WHERE status = 'active'")
    employees_with_salary = cursor.fetchall()
    
    salary_records = []
    for employee_id, base_monthly_salary in employees_with_salary:
        # 为每个员工生成最近12个月的薪资记录
        for month_offset in range(12):
            target_date = datetime.now() - timedelta(days=30 * month_offset)
            year = target_date.year
            month = target_date.month
            
            # 基础薪资有些波动
            base_salary = base_monthly_salary + random.randint(-1000, 1000)
            bonus = random.randint(0, 5000) if random.random() > 0.7 else 0  # 30%概率有奖金
            overtime_pay = random.randint(0, 2000) if random.random() > 0.8 else 0  # 20%概率有加班费
            deductions = random.randint(200, 800)  # 扣除项（保险、税等）
            total_amount = base_salary + bonus + overtime_pay - deductions
            
            salary_records.append((employee_id, year, month, base_salary, bonus, overtime_pay, total_amount, deductions))
    
    # 批量插入薪资记录
    try:
        cursor.executemany("""
            INSERT INTO salaries (employee_id, year, month, base_salary, bonus, overtime_pay, total_amount, deductions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, salary_records)
        print(f"✅ 已插入 {len(salary_records)} 条薪资记录")
    except mysql.connector.Error as e:
        print(f"⚠️ 插入薪资数据时出现重复，已跳过: {e}")
    
    print("🎉 MySQL示例数据生成完成！")

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        
        conn.close()
        print(f"✅ MySQL连接测试成功！员工总数: {count}")
        return True
    except Exception as e:
        print(f"❌ MySQL连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始初始化MySQL数据库...")
    init_mysql_database()
    test_mysql_connection() 